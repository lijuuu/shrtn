"""
Excel file processing for bulk URL operations.
"""
import uuid
import logging
import pandas as pd
import io
from typing import List, Dict, Any, Tuple
from django.core.files.uploadedfile import UploadedFile
from core.s3.connection import S3Connection
from core.utils.shortcode_generator import ShortcodeGenerator
from core.dependencies.service_registry import service_registry
from datetime import datetime

logger = logging.getLogger(__name__)


class ExcelProcessor:
    """Processes Excel files for bulk URL operations."""
    
    def __init__(self):
        self.s3_connection = S3Connection()
        self.shortcode_generator = ShortcodeGenerator()
    
    def process_bulk_urls(self, excel_file: UploadedFile, namespace_id: uuid.UUID, 
                         user_id: uuid.UUID, method: str = 'random') -> Dict[str, Any]:
        """
        Process Excel file with URLs and return shortened URLs.
        
        Expected Excel format:
        - Column A: Shortcode
        - Column B: Namespace
        - Column C: Long URLs
        """
        try:
            # Read Excel file using openpyxl directly to avoid pandas/numpy issues
            excel_file.seek(0)
            import openpyxl
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active
            
            # Convert to list of dictionaries (avoiding pandas for now)
            data = []
            headers = None
            
            for row in ws.iter_rows(values_only=True):
                if any(cell is not None for cell in row):  # Skip empty rows
                    if headers is None:
                        # First non-empty row is headers
                        headers = [str(cell) if cell is not None else '' for cell in row]
                    else:
                        # Data row
                        row_data = [str(cell) if cell is not None else '' for cell in row]
                        if len(row_data) >= len(headers):
                            # Create dictionary
                            row_dict = {}
                            for i, header in enumerate(headers):
                                row_dict[header] = row_data[i] if i < len(row_data) else ''
                            data.append(row_dict)
            
            if not data:
                raise ValueError("Excel file is empty or has no data rows")
            
            # Validate columns
            if not data or len(data[0]) < 3:
                raise ValueError("Excel file must have at least 3 columns: shortcode, namespace, longurls")
            
            # Process URLs
            results = []
            errors = []
            
            for index, row in enumerate(data):
                try:
                    # Get values by column name (case insensitive)
                    shortcode = row.get('shortcode', '').strip()
                    namespace_name = row.get('namespace', '').strip()
                    original_url = row.get('longurls', '').strip()
                    
                    # Validate required fields
                    if not shortcode or shortcode == 'nan':
                        errors.append(f"Row {index + 2}: Empty shortcode")
                        continue
                    
                    if not namespace_name or namespace_name == 'nan':
                        errors.append(f"Row {index + 2}: Empty namespace")
                        continue
                    
                    if not original_url or original_url == 'nan':
                        errors.append(f"Row {index + 2}: Empty URL")
                        continue
                    
                    # Validate shortcode format
                    import re
                    if not re.match(r'^[a-zA-Z0-9_-]+$', shortcode):
                        errors.append(f"Row {index + 2}: Invalid shortcode format '{shortcode}'")
                        continue
                    
                    # Validate URL format
                    url_pattern = re.compile(
                        r'^https?://'  # http:// or https://
                        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                        r'localhost|'  # localhost...
                        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                        r'(?::\d+)?'  # optional port
                        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                    
                    if not url_pattern.match(original_url):
                        errors.append(f"Row {index + 2}: Invalid URL format '{original_url}'")
                        continue
                    
                    # Get namespace ID from namespace name
                    namespace_service = service_registry.get_namespace_service()
                    target_namespace = namespace_service.get_by_name(namespace_name)
                    if not target_namespace:
                        errors.append(f"Row {index + 2}: Namespace '{namespace_name}' not found")
                        continue
                    
                    target_namespace_id = target_namespace.namespace_id
                    
                    # Check if shortcode already exists in target namespace
                    if not self.shortcode_generator.is_shortcode_available(target_namespace_id, shortcode):
                        errors.append(f"Row {index + 2}: Shortcode '{shortcode}' already exists in namespace '{namespace_name}'")
                        continue
                    
                    # Create URL data
                    url_data = {
                        'namespace_id': target_namespace_id,
                        'shortcode': shortcode,
                        'original_url': original_url,
                        'created_by_user_id': user_id,
                        'tags': [],
                        'is_private': False,
                        'is_active': True
                    }
                    
                    # Create URL in database
                    url_service = service_registry.get_url_service()
                    short_url = url_service.create(url_data)
                    
                    results.append({
                        'row': index + 2,
                        'original_url': original_url,
                        'shortcode': shortcode,
                        'short_url': f"/{shortcode}",
                        'tags': tags,
                        'status': 'success'
                    })
                    
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")
                    logger.error("Error processing row %d: %s", index + 2, e)
            
            # Create result Excel file
            result_df = self._create_result_dataframe(results)
            excel_buffer = self._create_excel_file(result_df)
            
            # Upload result file to S3
            file_key = f"bulk-results/{uuid.uuid4()}.xlsx"
            upload_success = self.s3_connection.upload_fileobj(
                excel_buffer, file_key, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            if not upload_success:
                raise Exception("Failed to upload result file to S3")
            
            # Generate presigned URL for download
            download_url = self.s3_connection.generate_presigned_url(file_key, expiration=3600)
            
            return {
                'success': True,
                'processed_count': len(results),
                'error_count': len(errors),
                'results': results,
                'errors': errors,
                'download_url': download_url,
                'file_key': file_key
            }
            
        except Exception as e:
            logger.error("Failed to process bulk URLs: %s", e)
            return {
                'success': False,
                'error': str(e),
                'processed_count': 0,
                'error_count': 0,
                'results': [],
                'errors': [str(e)]
            }
    
    def _create_result_dataframe(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create DataFrame for result Excel file."""
        data = []
        
        for result in results:
            data.append({
                'Original URL': result['original_url'],
                'Short Code': result['shortcode'],
                'Short URL': result['short_url'],
                'Tags': ', '.join(result['tags']),
                'Status': result['status']
            })
        
        return pd.DataFrame(data)
    
    def _create_excel_file(self, df: pd.DataFrame) -> io.BytesIO:
        """Create Excel file from DataFrame."""
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Shortened URLs')
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Shortened URLs']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        buffer.seek(0)
        return buffer
    
    def validate_excel_file(self, excel_file: UploadedFile) -> Dict[str, Any]:
        """Validate Excel file format."""
        try:
            df = pd.read_excel(excel_file)
            
            if df.empty:
                return {'valid': False, 'error': 'Excel file is empty'}
            
            if len(df.columns) < 1:
                return {'valid': False, 'error': 'Excel file must have at least one column (URLs)'}
            
            # Check for valid URLs in first column
            url_column = df.iloc[:, 0]
            valid_urls = 0
            invalid_urls = []
            
            for index, url in enumerate(url_column):
                if pd.notna(url) and str(url).strip():
                    valid_urls += 1
                else:
                    invalid_urls.append(index + 2)  # +2 for header and 1-based indexing
            
            return {
                'valid': True,
                'total_rows': len(df),
                'valid_urls': valid_urls,
                'invalid_urls': len(invalid_urls),
                'invalid_rows': invalid_urls,
                'columns': list(df.columns)
            }
            
        except Exception as e:
            logger.error("Failed to validate Excel file: %s", e)
            return {'valid': False, 'error': str(e)}
    
    def get_template_excel(self) -> bytes:
        """Generate template Excel file for bulk URL upload."""
        template_data = {
            'shortcode': [
                'example-link',
                'google-search',
                'github-repo'
            ],
            'namespace': [
                'main',
                'main',
                'dev'
            ],
            'longurls': [
                'https://example.com/page1',
                'https://google.com',
                'https://github.com/user/repo'
            ]
        }
        
        df = pd.DataFrame(template_data)
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='URLs')
            
            # Add instructions sheet
            instructions_data = {
                'Column': ['shortcode', 'namespace', 'longurls'],
                'Description': [
                    'Custom shortcode for the URL (required)',
                    'Target namespace name (required)',
                    'Original URL to be shortened (required)'
                ],
                'Rules': [
                    '2+ characters, letters, numbers, hyphens, underscores only',
                    'Must exist in your organization',
                    'Must be valid (http:// or https://)'
                ],
                'Example': [
                    'example-link',
                    'main',
                    'https://example.com/page1'
                ]
            }
            
            instructions_df = pd.DataFrame(instructions_data)
            instructions_df.to_excel(writer, index=False, sheet_name='Instructions')
        
        buffer.seek(0)
        return buffer.getvalue()
