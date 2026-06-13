# Phase 2 — Core Feature APIs

## Corrected Schema

### New Models

#### CheckIn
| Field | Type | Notes |
|-------|------|-------|
| `user` | FK → User | Who checked in |
| `hub` | FK → Hub | Which hub |
| `timestamp` | DateTimeField | When checked in |
| `people_count` | PositiveIntegerField | Group size |
| `status` | CharField | `safe`, `need_assistance` |
| `road_access` | CharField | `open`, `blocked`, `unknown` |
| `medical_notes` | TextField | Urgent medical needs |
| `latitude` | Decimal(9,6) | GPS from device |
| `longitude` | Decimal(9,6) | GPS from device |
| `channel` | CharField | `app`, `whatsapp`, `sms` |
| `client_uuid` | CharField, unique | Offline sync |

#### Comment
| Field | Type | Notes |
|-------|------|-------|
| `hazard` | FK → Hazard | Parent hazard |
| `user` | FK → User | Author |
| `body` | TextField | Content |
| `created_at` | DateTimeField | Auto |

#### Broadcast
| Field | Type | Notes |
|-------|------|-------|
| `hub` | FK → Hub | Targeted hub |
| `sender` | FK → User | Coordinator |
| `subject` | CharField | Short title |
| `body` | TextField | Message content |
| `priority` | CharField | `info`, `warning`, `urgent` |
| `created_at` | DateTimeField | Auto |

#### BroadcastRead
| Field | Type | Notes |
|-------|------|-------|
| `broadcast` | FK → Broadcast | |
| `user` | FK → User | Reader |
| `read_at` | DateTimeField | When read |

#### Notification
| Field | Type | Notes |
|-------|------|-------|
| `user` | FK → User | Recipient |
| `hub` | FK → Hub, nullable | Scope |
| `type` | CharField | `broadcast`, `alert`, `booking`, `hub_status` |
| `title` | CharField | Short title |
| `body` | TextField | Message |
| `read` | BooleanField | Default False |
| `link` | CharField, nullable | Deep link |
| `created_at` | DateTimeField | Auto |

### Modified Models

**Hazard** — already has `severity`, `source`, `client_uuid` ✅
**Booking** — already has `client_uuid` ✅
**Booking** — add `check_in_time` (DateTimeField, nullable), `people_count` (PositiveIntegerField, default 1)

---

## Segment Breakdown

### Segment 1: Hubs API
**Files:** `apps/hubs/`
**Endpoints:** CRUD + status update + coordinator assignment
**Views:** `HubListCreateView`, `HubDetailView`, `HubStatusUpdateView`, `HubCoordinatorAssignView`

### Segment 2: Hazards API
**Files:** `apps/hazards/`
**Endpoints:** Report, list, detail, clear, filter by category/severity/status
**Views:** `HazardListCreateView`, `HazardDetailView`, `HazardClearView`

### Segment 3: Bookings API
**Files:** `apps/bookings/`
**Endpoints:** Create booking, list my bookings, cancel, check-in
**Views:** `BookingCreateView`, `BookingListView`, `BookingCancelView`, `BookingCheckInView`

### Segment 4: Comms API
**Files:** `apps/comms/`
**Endpoints:** Broadcast (coordinator), CheckIn, Comments, Notifications
**Views:** `BroadcastListCreateView`, `BroadcastMarkReadView`, `CheckInListCreateView`, `CommentListCreateView`, `NotificationListView`, `NotificationMarkReadView`

### Segment 5: Dashboard API
**Files:** `apps/dashboard/` (new) or existing apps
**Endpoints:** Overview stats, map data, AI reports list
**All read-only aggregation — no new models**

### Segment 6: Admin API
**Files:** `apps/users/` (extend existing)
**Endpoints:** User list/search, hub management, message review, reports center
**Extends existing auth admin endpoints**

---

## Strict Rules
1. `client_uuid` on Hazard, CheckIn, Booking for offline sync
2. BookingService capacity validator: max 5 per 30-min slot per hub
3. Dashboard = read-only aggregation queries, no CRUD models
4. Broadcasts/Notifications trigger Celery tasks (`send_broadcast_task.delay()`)
5. View → Serializer → Service pattern enforced
6. `@extend_schema` on every view for Swagger
