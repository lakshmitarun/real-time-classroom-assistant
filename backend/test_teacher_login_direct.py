from auth_service_mongodb import AuthServiceMongoDB

auth_service = AuthServiceMongoDB()

# Test login with the teacher credentials
result, status = auth_service.login('lakshmitaruntarun@gmail.com', 'tarun123')
print(f"Status: {status}")
print(f"Result: {result}")
