# Authentication Service Contract

**Service**: User Authentication  
**Purpose**: Handle web interface authentication and credential management

## Methods

### authenticate(username: str, password: str) -> UserSession

Authenticates a user and creates a session.

**Parameters**:
- `username` (str): Login username
- `password` (str): Login password (plain text)

**Returns**: UserSession object if successful

**Behavior**:
1. Load credentials from `data/credentials.json`
2. Hash provided password using SHA256
3. Compare hash with stored password_hash
4. If match, create UserSession with session_id
5. Return UserSession
6. If no match, raise AuthenticationError

**Errors**:
- `AuthenticationError`: Invalid username or password
- `CredentialsNotFoundError`: No credentials file exists (first run)

### create_credentials(username: str, password: str) -> bool

Creates initial user credentials (first-time setup).

**Parameters**:
- `username` (str): Username to create
- `password` (str): Password to create (plain text)

**Returns**: True if created successfully

**Behavior**:
1. Check if credentials.json already exists
2. If exists, raise CredentialsExistError
3. Hash password using SHA256
4. Create credentials.json with username and hash
5. Return True

**Errors**:
- `CredentialsExistError`: Credentials already exist
- `StorageError`: Cannot write credentials file

### change_password(username: str, old_password: str, new_password: str) -> bool

Changes user password.

**Parameters**:
- `username` (str): Username
- `old_password` (str): Current password
- `new_password` (str): New password (plain text)

**Returns**: True if changed successfully

**Behavior**:
1. Authenticate with old_password
2. Hash new_password
3. Update credentials.json
4. Return True

**Errors**:
- `AuthenticationError`: Old password incorrect
- `CredentialsNotFoundError`: No credentials file

### validate_session(session_id: str) -> bool

Validates if a session is still active.

**Parameters**:
- `session_id` (str): Session identifier

**Returns**: True if session is valid, False otherwise

**Behavior**:
- Check if session exists in memory
- Check if session hasn't expired (timeout)
- Return True if valid, False otherwise

### logout(session_id: str) -> bool

Logs out a user session.

**Parameters**:
- `session_id` (str): Session identifier

**Returns**: True if logged out successfully

**Behavior**:
- Remove session from memory
- Return True

