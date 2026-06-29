# Phase 3: Design Database

This API uses MongoDB with two collections: `users` and `expenses`.

## Collection 1: Users

Example document:

```json
{
  "_id": "123",
  "username": "roshini",
  "email": "roshini@gmail.com",
  "password": "hashed_password"
}
```

Fields:
- `_id`: string or ObjectId, unique user identifier
- `username`: string, unique username
- `email`: string, unique email address
- `password`: string, hashed password

## Collection 2: Expenses

Example document:

```json
{
  "_id": "456",
  "user_id": "123",
  "title": "Lunch",
  "amount": 200,
  "category": "Food",
  "date": "2026-06-15"
}
```

Fields:
- `_id`: string or ObjectId, unique expense identifier
- `user_id`: string, reference to the owning user in `users`
- `title`: string, expense title or description
- `amount`: number, expense amount
- `category`: string, expense category
- `date`: string in ISO format (`YYYY-MM-DD`)

## Notes

- The `user_id` field in `expenses` links each expense to a user.
- Store `password` only as a hash; never save plain-text passwords.
- Dates should use ISO 8601 format for consistency.
