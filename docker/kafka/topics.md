# Kafka Topics

| Topic | Producer | Consumers | Partitions | Description |
|---|---|---|---|---|
| `user.registered` | auth-service | user-service, notification-service | 3 | Fired when a new user registers |
| `diary.entry.created` | diary-service | analytics-service, notification-service | 3 | Fired on every food log entry |
| `food.indexed` | food-service | ai-service | 3 | Fired when a food item is added/updated in the DB |
| `ai.food.recognized` | ai-service | diary-service | 3 | AI identified foods from a photo — diary creates draft entries |
| `analytics.report.ready` | analytics-service | notification-service | 1 | Weekly digest ready to send |

> **Partitioning key:** All user-scoped topics use `userId` as the Kafka message key
> to guarantee ordering per user.
