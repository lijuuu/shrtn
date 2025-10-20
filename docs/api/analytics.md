# Analytics API Documentation

## Overview
Analytics endpoints for tracking URL performance, click statistics, and detailed analytics data.

## Base URL
```
/api/v1/
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## Endpoints

### 1. Get URL Analytics
**GET** `/api/v1/organizations/{org_id}/namespaces/{namespace}/urls/{shortcode}/analytics/`

Get detailed analytics for a specific URL.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name
- `shortcode` (string, required) - URL shortcode

**Query Parameters:**
- `period` (string, optional) - Time period (1d, 7d, 30d, 90d, 1y, all) (default: 30d)
- `timezone` (string, optional) - Timezone (default: UTC)

**Response:**
```json
{
  "success": true,
  "payload": {
    "url": {
      "shortcode": "abc123",
      "original_url": "https://www.example.com",
      "title": "Example Website"
    },
    "summary": {
      "total_clicks": 1250,
      "unique_clicks": 980,
      "click_rate": 0.78,
      "last_clicked": "2024-01-01T15:30:00Z",
      "first_clicked": "2024-01-01T00:00:00Z"
    },
    "time_series": [
      {
        "date": "2024-01-01",
        "clicks": 45,
        "unique_clicks": 38
      },
      {
        "date": "2024-01-02",
        "clicks": 52,
        "unique_clicks": 41
      }
    ],
    "top_countries": [
      {
        "country": "United States",
        "code": "US",
        "clicks": 450,
        "percentage": 36.0
      },
      {
        "country": "United Kingdom",
        "code": "GB",
        "clicks": 280,
        "percentage": 22.4
      }
    ],
    "top_devices": [
      {
        "device": "Mobile",
        "clicks": 750,
        "percentage": 60.0
      },
      {
        "device": "Desktop",
        "clicks": 400,
        "percentage": 32.0
      },
      {
        "device": "Tablet",
        "clicks": 100,
        "percentage": 8.0
      }
    ],
    "top_browsers": [
      {
        "browser": "Chrome",
        "clicks": 600,
        "percentage": 48.0
      },
      {
        "browser": "Safari",
        "clicks": 300,
        "percentage": 24.0
      },
      {
        "browser": "Firefox",
        "clicks": 200,
        "percentage": 16.0
      }
    ],
    "referrers": [
      {
        "referrer": "https://www.google.com",
        "clicks": 150,
        "percentage": 12.0
      },
      {
        "referrer": "https://www.facebook.com",
        "clicks": 100,
        "percentage": 8.0
      }
    ]
  }
}
```

---

### 2. Get Namespace Analytics
**GET** `/api/v1/organizations/{org_id}/namespaces/{namespace}/analytics/`

Get analytics for all URLs in a namespace.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name

**Query Parameters:**
- `period` (string, optional) - Time period (1d, 7d, 30d, 90d, 1y, all) (default: 30d)
- `timezone` (string, optional) - Timezone (default: UTC)

**Response:**
```json
{
  "success": true,
  "payload": {
    "namespace": {
      "name": "marketing",
      "url_count": 25
    },
    "summary": {
      "total_clicks": 5000,
      "unique_clicks": 3500,
      "click_rate": 0.70,
      "total_urls": 25,
      "active_urls": 20
    },
    "top_urls": [
      {
        "shortcode": "abc123",
        "title": "Main Landing Page",
        "clicks": 1200,
        "unique_clicks": 900
      },
      {
        "shortcode": "def456",
        "title": "Product Page",
        "clicks": 800,
        "unique_clicks": 600
      }
    ],
    "time_series": [
      {
        "date": "2024-01-01",
        "clicks": 200,
        "unique_clicks": 150
      }
    ],
    "top_countries": [
      {
        "country": "United States",
        "code": "US",
        "clicks": 2000,
        "percentage": 40.0
      }
    ]
  }
}
```

---

### 3. Get Realtime Statistics
**GET** `/api/v1/organizations/{org_id}/namespaces/{namespace}/analytics/realtime/`

Get real-time analytics data.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID
- `namespace` (string, required) - Namespace name

**Response:**
```json
{
  "success": true,
  "payload": {
    "namespace": {
      "name": "marketing"
    },
    "realtime": {
      "clicks_last_hour": 25,
      "clicks_last_24h": 450,
      "active_users": 12,
      "top_urls_last_hour": [
        {
          "shortcode": "abc123",
          "title": "Main Landing Page",
          "clicks": 15
        }
      ],
      "recent_clicks": [
        {
          "shortcode": "abc123",
          "country": "United States",
          "device": "Mobile",
          "browser": "Chrome",
          "timestamp": "2024-01-01T15:30:00Z"
        }
      ]
    }
  }
}
```

---

### 4. Get Country Analytics
**GET** `/api/v1/organizations/{org_id}/analytics/countries/`

Get analytics data by country for the organization.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID

**Query Parameters:**
- `period` (string, optional) - Time period (1d, 7d, 30d, 90d, 1y, all) (default: 30d)
- `limit` (integer, optional) - Number of countries to return (default: 20)

**Response:**
```json
{
  "success": true,
  "payload": {
    "organization": {
      "id": "uuid",
      "name": "Organization Name"
    },
    "summary": {
      "total_clicks": 10000,
      "unique_countries": 45
    },
    "countries": [
      {
        "country": "United States",
        "code": "US",
        "clicks": 4000,
        "unique_clicks": 3000,
        "percentage": 40.0,
        "growth": 0.15
      },
      {
        "country": "United Kingdom",
        "code": "GB",
        "clicks": 2000,
        "unique_clicks": 1500,
        "percentage": 20.0,
        "growth": 0.08
      },
      {
        "country": "Canada",
        "code": "CA",
        "clicks": 1000,
        "unique_clicks": 800,
        "percentage": 10.0,
        "growth": 0.12
      }
    ],
    "time_series": [
      {
        "date": "2024-01-01",
        "countries": [
          {
            "country": "United States",
            "clicks": 150
          },
          {
            "country": "United Kingdom",
            "clicks": 75
          }
        ]
      }
    ]
  }
}
```

---

### 5. Get Tier Analytics
**GET** `/api/v1/organizations/{org_id}/analytics/tiers/`

Get analytics data by user tier for the organization.

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `org_id` (uuid, required) - Organization ID

**Query Parameters:**
- `period` (string, optional) - Time period (1d, 7d, 30d, 90d, 1y, all) (default: 30d)

**Response:**
```json
{
  "success": true,
  "payload": {
    "organization": {
      "id": "uuid",
      "name": "Organization Name"
    },
    "summary": {
      "total_clicks": 10000,
      "total_users": 150
    },
    "tiers": [
      {
        "tier": "free",
        "users": 100,
        "clicks": 3000,
        "percentage": 30.0,
        "avg_clicks_per_user": 30
      },
      {
        "tier": "premium",
        "users": 40,
        "clicks": 5000,
        "percentage": 50.0,
        "avg_clicks_per_user": 125
      },
      {
        "tier": "enterprise",
        "users": 10,
        "clicks": 2000,
        "percentage": 20.0,
        "avg_clicks_per_user": 200
      }
    ],
    "time_series": [
      {
        "date": "2024-01-01",
        "tiers": [
          {
            "tier": "free",
            "clicks": 100
          },
          {
            "tier": "premium",
            "clicks": 200
          },
          {
            "tier": "enterprise",
            "clicks": 50
          }
        ]
      }
    ]
  }
}
```

---

## Analytics Data Types

### Click Data:
- **Total Clicks**: Total number of clicks
- **Unique Clicks**: Number of unique users who clicked
- **Click Rate**: Ratio of unique clicks to total clicks
- **Growth Rate**: Percentage change from previous period

### Geographic Data:
- **Country**: Country name and code
- **Region**: Geographic region
- **City**: City name (if available)

### Device Data:
- **Device Type**: Mobile, Desktop, Tablet
- **Operating System**: iOS, Android, Windows, macOS, Linux
- **Browser**: Chrome, Safari, Firefox, Edge, etc.

### Referrer Data:
- **Referrer**: Source website or app
- **Campaign**: Marketing campaign identifier
- **Medium**: Traffic source medium (organic, social, email, etc.)

### Time-based Data:
- **Time Series**: Data points over time
- **Hourly**: Clicks per hour
- **Daily**: Clicks per day
- **Weekly**: Clicks per week
- **Monthly**: Clicks per month

---

## Time Periods

### Available Periods:
- `1d` - Last 24 hours
- `7d` - Last 7 days
- `30d` - Last 30 days (default)
- `90d` - Last 90 days
- `1y` - Last year
- `all` - All time

### Timezone Support:
- All timestamps are returned in the specified timezone
- Default timezone is UTC
- Supported timezones: All standard timezone identifiers

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Invalid time period",
  "errors": [
    "Time period must be one of: 1d, 7d, 30d, 90d, 1y, all"
  ]
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "message": "Authentication required",
  "status_code": 401
}
```

### 403 Forbidden
```json
{
  "success": false,
  "message": "Insufficient permissions",
  "status_code": 403
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "URL not found",
  "status_code": 404
}
```

---

## Rate Limiting

- Analytics queries: 100 requests per hour per user
- Realtime analytics: 50 requests per hour per user
- Country analytics: 20 requests per hour per user
- Tier analytics: 20 requests per hour per user

---

## Data Retention

### Click Data:
- **Raw Data**: 2 years
- **Aggregated Data**: 5 years
- **Real-time Data**: 24 hours

### Privacy:
- IP addresses are anonymized
- Personal data is not stored
- Geographic data is country-level only

---

## Notes

- Analytics data is updated in real-time
- Historical data may take up to 1 hour to appear
- All timestamps are in ISO 8601 format
- Percentages are rounded to 1 decimal place
- Growth rates are calculated as percentage change from previous period
- Analytics data is cached for 5 minutes to improve performance
