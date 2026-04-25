# Roll-based Access Control (RBAC)

## Overview

Role-based access control (RBAC) is a method of regulating access to computer or network resources 
based on the roles of individual users within an enterprise. RBAC allows administrators to assign 
permissions to specific roles, and then assign those roles to users, thereby controlling access to 
resources based on the user's role within the organization.

## Matrix

### Roles and Permissions

| Permission                      | Admin | User | Unauthenticated |
|---------------------------------|-------|------|-----------------|
| Create Garden                   | ✅     | ✅    | ❌               |
| Edit own Garden                 | ✅     | ✅    | N/A             |
| Edit any Garden                 | ✅     | ❌    | ❌               |
| Delete own Garden               | ✅     | ✅    | N/A             |
| Delete any Garden               | ✅     | ❌    | ❌               |
| View own Garden                 | ✅     | ✅    | N/A             |
| View any Garden                 | ✅     | ✅    | ❌               |
| View public Gardens             | ✅     | ✅    | ✅               |
| Update own Garden               | ✅     | ✅    | N/A             |
| Update any Garden               | ✅     | ❌    | ❌               |
| Create Plant in own Garden      | ✅     | ✅    | N/A             |
| Create Plant in any Garden      | ✅     | ❌    | ❌               |
| View own Plant                  | ✅     | ✅    | N/A             |
| View any Plant                  | ✅     | ✅    | ❌               |
| View any Plant in public Garden | ✅     | ✅    | ✅               |
| Update own Plant                | ✅     | ✅    | N/A             |
| Update any Plant                | ✅     | ❌    | ❌               |
| Delete own Plant                | ✅     | ✅    | N/A             |
| Delete any Plant                | ✅     | ❌    | ❌               |
| Generate AI Plant Description   | ✅     | ✅    | ❌               |


# Garden Guest Member Permissions

| Permission                                         | Guest  |
|----------------------------------------------------|--------|
| View membership Garden                             | ✅      |
| Update membership Garden                           | ❌      |
| Delete membership Garden                           | ❌      |
| Create Plant in membership Garden                  | ✅      |
| View Plant in membership Garden                    | ✅      |
| Update Plant in membership Garden                  | ✅      |
| Delete Plant in membership Garden                  | ❌      |
| Generate AI Plant Description in membership Garden | ✅      |
