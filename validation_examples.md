# User Validation Examples

## 🔍 Comprehensive Field Validation in Serializers

### **1. UserCreateSerializer Validation**

#### **Valid Request Example ✅**
```json
POST /api/users/create/
{
    "email": "john.doe@example.com",
    "name": "John Doe",
    "username": "johndoe123",
    "password": "SecurePass123!"
}

// Response
{
    "id": 1,
    "email": "john.doe@example.com",
    "name": "John Doe",
    "username": "johndoe123",
    "verified": false,
    "created_at": "2024-01-01T00:00:00Z",
    "message": "User created successfully"
}
```

#### **Invalid Request Examples ❌**

**Missing Required Fields:**
```json
POST /api/users/create/
{
    "email": "john@example.com"
    // Missing name, username, password
}

// Response
{
    "error": "Validation failed",
    "details": {
        "name": ["This field is required."],
        "username": ["This field is required."],
        "password": ["This field is required."]
    }
}
```

**Invalid Email Format:**
```json
POST /api/users/create/
{
    "email": "invalid-email",
    "name": "John Doe",
    "username": "johndoe",
    "password": "SecurePass123!"
}

// Response
{
    "error": "Validation failed",
    "details": {
        "email": ["Enter a valid email address"]
    }
}
```

**Weak Password:**
```json
POST /api/users/create/
{
    "email": "john@example.com",
    "name": "John Doe",
    "username": "johndoe",
    "password": "123"
}

// Response
{
    "error": "Validation failed",
    "details": {
        "password": [
            "Password must be at least 8 characters long",
            "Password must contain at least one uppercase letter",
            "Password must contain at least one lowercase letter",
            "Password must contain at least one number",
            "Password must contain at least one special character"
        ]
    }
}
```

**Invalid Username Format:**
```json
POST /api/users/create/
{
    "email": "john@example.com",
    "name": "John Doe",
    "username": "john@doe",  // Contains @ symbol
    "password": "SecurePass123!"
}

// Response
{
    "error": "Validation failed",
    "details": {
        "username": ["Username can only contain letters, numbers, and underscores"]
    }
}
```

**Invalid Name Format:**
```json
POST /api/users/create/
{
    "email": "john@example.com",
    "name": "John123Doe",  // Contains numbers
    "username": "johndoe",
    "password": "SecurePass123!"
}

// Response
{
    "error": "Validation failed",
    "details": {
        "name": ["Name can only contain letters, spaces, hyphens, apostrophes, and periods"]
    }
}
```

**Duplicate Email:**
```json
POST /api/users/create/
{
    "email": "existing@example.com",  // Already exists
    "name": "John Doe",
    "username": "johndoe",
    "password": "SecurePass123!"
}

// Response
{
    "error": "Validation failed",
    "details": {
        "email": ["A user with this email already exists"]
    }
}
```

**Cross-Field Validation (Username = Email Prefix):**
```json
POST /api/users/create/
{
    "email": "johndoe@example.com",
    "name": "John Doe",
    "username": "johndoe",  // Same as email prefix
    "password": "SecurePass123!"
}

// Response
{
    "error": "Validation failed",
    "details": {
        "username": ["Username cannot be the same as email prefix"]
    }
}
```

### **2. UserUpdateSerializer Validation**

#### **Valid Update Example ✅**
```json
PUT /api/users/1/update/
{
    "name": "John Smith",
    "verified": true
}

// Response
{
    "id": 1,
    "email": "john@example.com",
    "name": "John Smith",
    "username": "johndoe",
    "verified": true,
    "is_active": true,
    "message": "User updated successfully"
}
```

#### **Invalid Update Examples ❌**

**Duplicate Email (Different User):**
```json
PUT /api/users/1/update/
{
    "email": "other@example.com"  // Already exists for another user
}

// Response
{
    "error": "Validation failed",
    "details": {
        "email": ["A user with this email already exists"]
    }
}
```

### **3. UserPasswordChangeSerializer Validation**

#### **Valid Password Change ✅**
```json
POST /api/users/1/change-password/
{
    "current_password": "OldPass123!",
    "new_password": "NewSecurePass456!",
    "confirm_password": "NewSecurePass456!"
}

// Response
{
    "message": "Password changed successfully"
}
```

#### **Invalid Password Change Examples ❌**

**Passwords Don't Match:**
```json
POST /api/users/1/change-password/
{
    "current_password": "OldPass123!",
    "new_password": "NewSecurePass456!",
    "confirm_password": "DifferentPass789!"
}

// Response
{
    "error": "Validation failed",
    "details": {
        "confirm_password": ["New password and confirm password do not match"]
    }
}
```

**Same as Current Password:**
```json
POST /api/users/1/change-password/
{
    "current_password": "OldPass123!",
    "new_password": "OldPass123!",
    "confirm_password": "OldPass123!"
}

// Response
{
    "error": "Validation failed",
    "details": {
        "new_password": ["New password must be different from current password"]
    }
}
```

## 🛡️ Validation Rules Summary

### **Email Validation:**
- ✅ Must be valid email format
- ✅ Must be unique across all users
- ✅ Automatically converted to lowercase
- ✅ Whitespace trimmed

### **Username Validation:**
- ✅ 3-150 characters long
- ✅ Only letters, numbers, and underscores
- ✅ Must be unique across all users
- ✅ Cannot be same as email prefix
- ✅ Automatically converted to lowercase

### **Name Validation:**
- ✅ 2-255 characters long
- ✅ Only letters, spaces, hyphens, apostrophes, and periods
- ✅ Whitespace trimmed

### **Password Validation:**
- ✅ 8-128 characters long
- ✅ At least one uppercase letter
- ✅ At least one lowercase letter
- ✅ At least one number
- ✅ At least one special character
- ✅ Cannot be same as current password (for updates)

### **Cross-Field Validation:**
- ✅ Username cannot be same as email prefix
- ✅ New password must match confirm password
- ✅ New password must be different from current password

## 🎯 Benefits of This Validation:

1. **Security**: Strong password requirements
2. **Data Integrity**: Unique constraints and format validation
3. **User Experience**: Clear error messages
4. **Consistency**: Standardized data format
5. **Flexibility**: Different validation for create vs update
6. **Comprehensive**: Field-level and cross-field validation
