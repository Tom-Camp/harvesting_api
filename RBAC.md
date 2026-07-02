# Roll-based Access Control (RBAC)

## Overview

Role-based access control (RBAC) is a method of regulating access to computer or network resources
based on the roles of individual users within an enterprise. RBAC allows administrators to assign
permissions to specific roles, and then assign those roles to users, thereby controlling access to
resources based on the user's role within the organization.

## Matrix

Admins receive a synthetic Owner membership on any garden, giving them full access regardless of
explicit membership.

### System Role Permissions

| Permission                | Admin | User (member) | Unauthenticated |
|---------------------------|-------|---------------|-----------------|
| Create Garden             | Y     | Y             | N               |
| List accessible Gardens   | Y     | Y             | N               |
| View Garden               | Y     | Y             | N               |
| Update Garden             | Y     | Owner only    | N               |
| Delete Garden             | Y     | Owner only    | N               |
| List Garden Members       | Y     | Y             | N               |
| Invite Member             | Y     | Owner only    | N               |
| Remove Member             | Y     | Owner only    | N               |
| Accept Invitation         | Y     | Y             | N               |
| List Plants               | Y     | Y             | N               |
| Create Plant              | Y     | Y             | N               |
| View Plant                | Y     | Y             | N               |
| Update Plant              | Y     | Y             | N               |
| Archive / Unarchive Plant | Y     | Y             | N               |
| Delete Plant              | Y     | Owner only    | N               |
| Generate AI Care Info     | Y     | Y             | N               |
| Add Harvest               | Y     | Y             | N               |
| Update Harvest            | Y     | Y             | N               |
| Delete Harvest            | Y     | Y             | N               |
| Add Note                  | Y     | Y             | N               |
| Update Note               | Y     | Y             | N               |
| Delete Note               | Y     | Y             | N               |
| Read User                 | Y     | N             | N               |
| Update User               | Y     | N             | N               |
| List Users                | Y     | N             | N               |
| Create User               | Y     | N             | N               |
| Update User Roles         | Y     | N             | N               |
| Delete User               | Y     | N             | N               |
| Invite User               | Y     | N             | N               |
| Edit own User             | Y     | Y             | N               |



## Garden Member Permissions

Garden members have one of two roles: `owner` or `member`.

| Permission                | Owner | Member |
|---------------------------|-------|--------|
| View Garden               | Y     | Y      |
| Update Garden             | Y     | N      |
| Delete Garden             | Y     | N      |
| List Members              | Y     | Y      |
| Invite Member             | Y     | N      |
| Remove Member             | Y     | N      |
| List Plants               | Y     | Y      |
| Create Plant              | Y     | Y      |
| View Plant                | Y     | Y      |
| Update Plant              | Y     | Y      |
| Archive / Unarchive Plant | Y     | Y      |
| Delete Plant              | Y     | N      |
| Generate AI Care Info     | Y     | Y      |
| Add Harvest               | Y     | Y      |
| Update Harvest            | Y     | Y      |
| Delete Harvest            | Y     | Y      |
| Add Note                  | Y     | Y      |
| Update Note               | Y     | Y      |
| Delete Note               | Y     | Y      |
