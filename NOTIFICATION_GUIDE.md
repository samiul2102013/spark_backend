# ChargeSafe Push & In-App Notification System — Flutter Integration Guide

Base URL: `https://spark.kodevio.com` (or `http://spark.kodevio.com:8000` for dev)
All endpoints are prefixed with `/api/v1/`
Auth: Bearer JWT token (obtained from `/api/v1/auth/token/`)

---

## 1. Register Device Token (For Push Notifications)

Called once when the app starts (or when FCM token refreshes). Must be called before push will work.

**Endpoint:** `POST /api/v1/devices/register/`

**Request:**
```json
{
  "token": "dGhpcyBpcyBhIGZh...",
  "platform": "android"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `token` | string | FCM token from `firebase_messaging.getToken()` |
| `platform` | string | `"android"`, `"ios"`, or `"web"` (default: `"android"`) |

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "token": "dGhpcyBpcyBhIGZh...",
    "platform": "android",
    "is_active": true,
    "created_at": "2026-07-07T08:00:00+0000"
  },
  "message": "Created"
}
```

**Flutter Implementation:**
```dart
import 'package:firebase_messaging/firebase_messaging.dart';

Future<void> registerFCMToken() async {
  final fcm = FirebaseMessaging.instance;
  final token = await fcm.getToken();
  if (token == null) return;

  final response = await http.post(
    Uri.parse('$baseUrl/api/v1/devices/register/'),
    headers: {
      'Authorization': 'Bearer $jwtToken',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'token': token,
      'platform': Platform.isIOS ? 'ios' : 'android',
    }),
  );
}

// Listen for token refresh
FirebaseMessaging.instance.onTokenRefresh.listen((newToken) {
  // Call register endpoint again with new token
});
```

---

## 2. Unregister Device Token

Call when user logs out.

**Endpoint:** `DELETE /api/v1/devices/unregister/`

**Request:**
```json
{
  "token": "dGhpcyBpcyBhIGZh..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "message": "Device token deactivated."
  },
  "message": "Success"
}
```

---

## 3. List In-App Notifications

Fetches the notification history displayed in the app's notification bell/inbox.

**Endpoint:** `GET /api/v1/notifications/`

**Query Parameters (optional):**

| Param | Type | Description |
|-------|------|-------------|
| `unread_only` | bool | `true` to show only unread |
| `page` | int | Page number (default: 1) |
| `limit` | int | Items per page (default: 20, max: 100) |

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "user": "+18765551234",
        "hub": 1,
        "title": "Flood Alert",
        "message": "Flooding reported near your area. Stay safe.",
        "category": "alert",
        "data": {
          "hazard_id": "5",
          "category": "flood"
        },
        "link": null,
        "read": false,
        "sent_at": null,
        "created_at": "2026-07-07T08:00:00+0000"
      },
      {
        "id": 2,
        "user": "+18765551234",
        "hub": null,
        "title": "Hub Status: Critical",
        "message": "Your hub Kingston Emergency Hub is now critical.",
        "category": "hub_status",
        "data": {
          "hub_id": "1",
          "status": "critical"
        },
        "link": null,
        "read": true,
        "sent_at": null,
        "created_at": "2026-07-06T14:30:00+0000"
      }
    ]
  },
  "message": "Success"
}
```

**`category` field values:**

| Value | Meaning | UI Hint |
|-------|---------|---------|
| `alert` | Hazard/emergency alert | Red/warning icon |
| `broadcast` | Coordinator broadcast | Megaphone icon |
| `booking` | Booking confirmation/update | Calendar icon |
| `hub_status` | Hub status change (open/critical/low_battery) | Battery/location icon |

**Flutter Implementation:**
```dart
Future<List<NotificationModel>> fetchNotifications({bool unreadOnly = false}) async {
  final queryParams = <String, String>{
    if (unreadOnly) 'unread_only': 'true',
  };
  final uri = Uri.parse('$baseUrl/api/v1/notifications/')
      .replace(queryParameters: queryParams);
  
  final response = await http.get(uri, headers: {
    'Authorization': 'Bearer $jwtToken',
  });
  
  final body = jsonDecode(response.body);
  final results = body['data']['results'] as List;
  return results.map((json) => NotificationModel.fromJson(json)).toList();
}
```

---

## 4. Mark Single Notification as Read

**Endpoint:** `PATCH /api/v1/notifications/{id}/read/`

**Request:** No body needed.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user": "+18765551234",
    "hub": 1,
    "title": "Flood Alert",
    "message": "Flooding reported near your area.",
    "category": "alert",
    "data": {"hazard_id": "5"},
    "link": null,
    "read": true,
    "sent_at": null,
    "created_at": "2026-07-07T08:00:00+0000"
  },
  "message": "Success"
}
```

---

## 5. Mark All Notifications as Read

**Endpoint:** `POST /api/v1/notifications/read-all/`

**Request:** No body needed.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "marked_read": 5
  },
  "message": "Success"
}
```

**`marked_read`** indicates how many notifications were marked as read.

---

## 6. Unread Count (Derived)

There's no dedicated unread count endpoint. Calculate from the list response:

```dart
int getUnreadCount(List<NotificationModel> list) {
  return list.where((n) => !n.read).length;
}
```

Or use `GET /api/v1/notifications/?unread_only=true` and read the `count` field.

---

## 7. Receiving Push Notifications (FCM)

**Flutter Setup:**

```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class PushNotificationService {
  static final FirebaseMessaging _fcm = FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  static Future<void> init() async {
    // Request permission
    await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    // Initialize local notifications (for displaying when app is in foreground)
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    await _localNotifications.initialize(
      const InitializationSettings(
        android: androidSettings,
        iOS: iosSettings,
      ),
    );

    // Get FCM token and register with backend
    final token = await _fcm.getToken();
    await _registerToken(token);

    // Listen for token refresh
    _fcm.onTokenRefresh.listen((newToken) {
      _registerToken(newToken);
    });

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Handle background tap (app opened from notification)
    FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);

    // Handle app opened from terminated state via notification
    final initialMessage = await _fcm.getInitialMessage();
    if (initialMessage != null) {
      _handleNotificationTap(initialMessage);
    }
  }

  static void _handleForegroundMessage(RemoteMessage message) {
    final notification = message.notification;
    if (notification == null) return;

    _localNotifications.show(
      notification.hashCode,
      notification.title,
      notification.body,
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'chargesafe_channel',
          'ChargeSafe Notifications',
          importance: Importance.high,
          priority: Priority.high,
        ),
        iOS: DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
      payload: jsonEncode(message.data),
    );
  }

  static void _handleNotificationTap(RemoteMessage message) {
    // Navigate based on message.data
    final data = message.data;
    if (data['hazard_id'] != null) {
      // Navigate to hazard detail screen
    } else if (data['checkin_id'] != null) {
      // Navigate to check-in detail
    }
  }
}
```

---

## Summary of All Endpoints

| # | Method | Endpoint | Purpose | Auth |
|---|--------|----------|---------|------|
| 1 | POST | `/api/v1/devices/register/` | Register FCM token | JWT |
| 2 | DELETE | `/api/v1/devices/unregister/` | Deactivate FCM token | JWT |
| 3 | GET | `/api/v1/notifications/` | List in-app notifications | JWT |
| 4 | PATCH | `/api/v1/notifications/{id}/read/` | Mark one as read | JWT |
| 5 | POST | `/api/v1/notifications/read-all/` | Mark all as read | JWT |

**What triggers notifications automatically (no Flutter action needed):**

| Trigger | What happens |
|---------|-------------|
| Hazard created | Alert sent to all hub residents |
| Hazard cleared | Sent to the original reporter |
| Comment on hazard | Sent to the hazard reporter |
| Check-in with "need_assistance" | Sent to coordinator + admins |
| Broadcast (warning/urgent) | Sent to all hub residents |
| Hub status change (critical/low_battery) | Sent to all hub residents |

---

## Testing Checklist

- [ ] Device token registered on login
- [ ] Token re-registered on refresh
- [ ] Token unregistered on logout
- [ ] Notification list fetches and paginates correctly
- [ ] Unread filter works
- [ ] Mark single notification as read (swipe/tap)
- [ ] Mark all as read (button)
- [ ] Push received when app is in foreground
- [ ] Push received when app is in background (notification tray)
- [ ] Notification tap navigates to correct screen
- [ ] Badge count updates correctly
