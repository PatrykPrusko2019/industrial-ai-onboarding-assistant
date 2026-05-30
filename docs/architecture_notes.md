# Architecture Notes

The application consists of the following main components:

- React frontend
- FastAPI backend
- PostgreSQL database
- AI/RAG service
- Document knowledge base
- Authentication and role-based access control
- Industrial safety analytics module
- Optional .NET Audit & Compliance Service

The system is designed as a cloud-ready application that can be deployed using containers.

# Authentication Flow

The application uses JWT-based authentication.

1. A new user creates an account using the registration form.
2. The backend hashes the password before saving the user in PostgreSQL.
3. During login, the backend verifies the password and returns a JWT token.
4. The frontend stores the token in localStorage.
5. Protected API requests include the token in the Authorization header.
6. The backend validates the token and resolves the current user.
7. User role determines access to selected features such as expert review and document management.

Roles:

- employee: standard onboarding user
- expert: domain expert who can review AI-generated answers
- admin: system administrator