// Create application database and user
db = db.getSiblingDB('app');

// Create collections with schema validation
db.createCollection('users', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['email', 'password_hash', 'created_at'],
            properties: {
                email: {
                    bsonType: 'string',
                    pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
                },
                password_hash: {
                    bsonType: 'string'
                },
                created_at: {
                    bsonType: 'date'
                },
                last_login: {
                    bsonType: 'date'
                }
            }
        }
    }
});

db.createCollection('logs', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['timestamp', 'level', 'message'],
            properties: {
                timestamp: {
                    bsonType: 'date'
                },
                level: {
                    enum: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                },
                message: {
                    bsonType: 'string'
                },
                metadata: {
                    bsonType: 'object'
                }
            }
        }
    }
});

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.logs.createIndex({ "timestamp": 1 });
db.logs.createIndex({ "level": 1 });

// Create admin user if not exists
if (db.users.countDocuments() === 0) {
    db.users.insertOne({
        email: 'admin@example.com',
        password_hash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFX1FgFI/qSF/AS', // Change this!
        created_at: new Date(),
        is_admin: true
    });
} 