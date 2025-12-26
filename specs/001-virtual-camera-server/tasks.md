# Tasks: Virtual Camera Server Application

**Input**: Design documents from `/specs/001-virtual-camera-server/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL and not requested in the feature specification. Focus on implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below follow the single project structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure: src/models/, src/services/, src/gui/, tests/unit/, tests/integration/, videos/, data/
- [ ] T002 Create virtual environment: python3 -m venv venv
- [x] T003 Create requirements.txt with dependencies: opencv-python, PyGObject
- [x] T004 [P] Create README.md with setup instructions from quickstart.md
- [x] T005 [P] Create .gitignore file excluding venv/, videos/, data/, __pycache__/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create JSON storage utility in src/services/storage.py for reading/writing JSON files (videos.json, cameras.json, credentials.json)
- [x] T007 Create error handling module in src/services/exceptions.py with custom exceptions: VideoNotFoundError, CameraNotFoundError, AuthenticationError, StreamError, etc.
- [x] T008 Create logging configuration in src/services/logger.py for application-wide logging
- [x] T009 Create UUID generation utility function in src/services/utils.py for generating unique IDs
- [x] T010 Create directory initialization function in src/services/storage.py to ensure videos/ and data/ directories exist

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Video Library and Single Virtual Camera (Priority: P1) 🎯 MVP

**Goal**: Upload videos to library and create a virtual camera that streams one video on repeat via RTSP

**Independent Test**: (1) Upload a video file programmatically, (2) Create a virtual camera instance that references that video, (3) Connect to the RTSP stream URL and observe the video playing on repeat

### Implementation for User Story 1

- [x] T011 [P] [US1] Create Video model in src/models/video.py with attributes: id, filename, file_path, file_size, duration, width, height, fps, format, upload_date, metadata
- [x] T012 [P] [US1] Create VirtualCamera model in src/models/virtual_camera.py with attributes: id, name, video_ids, rtsp_url, rtsp_port, auth_enabled, auth_username, auth_password_hash, status, current_video_index, created_date, last_modified
- [x] T013 [US1] Implement VideoLibraryService in src/services/video_library.py with methods: upload_video(), get_video(), list_videos(), get_video_file_path() (depends on T011, T006)
- [x] T014 [US1] Implement video metadata extraction using OpenCV in src/services/video_library.py to extract duration, width, height, fps, format from uploaded videos
- [x] T015 [US1] Implement CameraManagerService in src/services/camera_manager.py with methods: create_camera(), get_camera(), list_cameras(), get_camera_rtsp_url() (depends on T012, T013)
- [x] T016 [US1] Implement RTSP server service in src/services/rtsp_server.py with methods: start_stream(), stop_stream(), is_streaming() using GStreamer gst-rtsp-server (depends on T012, T013)
- [x] T017 [US1] Implement single video playback loop in src/services/rtsp_server.py that reads video with OpenCV, encodes to H.264 via GStreamer, and streams via RTSP with continuous repeat
- [x] T018 [US1] Create main.py entry point that initializes services and allows programmatic video upload and camera creation for testing (depends on T013, T015, T016)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - can upload video, create camera, and stream via RTSP

---

## Phase 4: User Story 2 - Web Interface with Basic Authentication (Priority: P2)

**Goal**: Provide web-based interface with authentication for uploading videos and managing virtual cameras

**Independent Test**: (1) Access web application in browser, (2) Provide valid credentials to authenticate, (3) Use web interface to upload a video file, (4) Use web interface to create and name a virtual camera

### Implementation for User Story 2

- [x] T019 [P] [US2] Create UserSession model in src/models/user_session.py with attributes: username, session_id, login_time, last_activity
- [x] T020 [P] [US2] Create UserCredentials storage structure (JSON schema) in data/credentials.json
- [x] T021 [US2] Implement AuthService in src/services/auth.py with methods: authenticate(), create_credentials(), validate_session(), logout() (depends on T006, T020)
- [x] T022 [US2] Create login page in src/web/templates/auth/login.html with username/password fields and login button (depends on T021)
- [x] T023 [US2] Create main dashboard in src/web/templates/dashboard/index.html with tabbed interface and navigation (depends on T022)
- [x] T024 [US2] Create video upload interface in web dashboard with file selection and upload button (depends on T013, T023)
- [x] T025 [US2] Create camera creator interface in web dashboard with name input, video selection list, and create button (depends on T015, T023)
- [x] T026 [US2] Create camera list display in web dashboard showing all cameras with their names and status (depends on T015, T023)
- [x] T027 [US2] Create video library display in web dashboard showing all upleos (depends on T013, T023)
- [x] T028 [US2] Update main.py to launch Flask web server with login page first, then doaded vidashboard after authentication (depends on T022, T023)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full web interface workflow for uploading videos and creating cameras

---

## Phase 5: User Story 3 - Multiple Videos on Repeat (Priority: P3)

**Goal**: Enable virtual cameras to play multiple videos sequentially in a continuous loop

**Independent Test**: (1) Have multiple videos in library, (2) Create virtual camera and assign multiple videos, (3) Connect to RTSP stream and observe videos playing sequentially in loop

### Implementation for User Story 3

- [x] T029 [US3] Update CameraManagerService.create_camera() in src/services/camera_manager.py to accept and validate multiple video_ids (depends on T015)
- [x] T030 [US3] Update RTSP server service in src/services/rtsp_server.py to handle multiple videos: play first video, when finished move to next, when last finished restart from first (depends on T016)
- [x] T031 [US3] Update camera creator interface in web dashboard to allow selecting multiple videos from library (multi-select checkboxes) (depends on T025)
- [x] T032 [US3] Update VirtualCamera model in src/models/virtual_camera.py to track current_video_index for sequential playback (already in model, ensure it's used correctly)
- [x] T033 [US3] Update RTSP server playback loop in src/services/rtsp_server.py to increment current_video_index and update camera status when switching videos (depends on T030)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - cameras can stream multiple videos sequentially

---

## Phase 6: User Story 4 - RTSP Stream Viewer Window (Priority: P4)

**Goal**: Provide built-in viewer window to preview RTSP streams from virtual cameras

**Independent Test**: (1) Create virtual camera that is actively streaming, (2) Open viewer window for that camera's RTSP stream, (3) Observe video playback in viewer

### Implementation for User Story 4

- [ ] T034 [US4] Create stream viewer page in web interface with video display area and RTSP client connection (depends on T016)
- [ ] T035 [US4] Implement RTSP client connection in web interface using HTML5 video player or WebRTC to connect to RTSP URL and display stream
- [ ] T036 [US4] Add "View Stream" button to camera list in web dashboard that opens viewer page for selected camera (depends on T026, T034)
- [ ] T037 [US4] Update stream viewer to handle stream disconnection and display error messages if stream unavailable (depends on T034, T035)
- [ ] T038 [US4] Update stream viewer to support multiple viewer windows for different cameras simultaneously (depends on T034)

**Checkpoint**: At this point, User Stories 1-4 should all work independently - can view RTSP streams in built-in viewer

---

## Phase 7: User Story 5 - RTSP Authentication (Priority: P5)

**Goal**: Enable RTSP stream authentication to secure virtual camera content

**Independent Test**: (1) Configure authentication credentials for RTSP stream, (2) Attempt to connect without credentials (should fail), (3) Connect with valid credentials (should succeed)

### Implementation for User Story 5

- [ ] T039 [US5] Update camera creator interface in web dashboard to include authentication checkbox and username/password fields (depends on T025)
- [ ] T040 [US5] Update CameraManagerService.create_camera() in src/services/camera_manager.py to handle auth_enabled, auth_username, and hash auth_password (depends on T015)
- [ ] T041 [US5] Implement RTSP authentication in src/services/rtsp_server.py using GStreamer RTSPAuth to require credentials for stream access (depends on T016)
- [ ] T042 [US5] Update RTSP server start_stream() in src/services/rtsp_server.py to configure authentication if camera.auth_enabled is True (depends on T041)
- [ ] T043 [US5] Update stream viewer in web interface to prompt for and use RTSP credentials when connecting to authenticated streams (depends on T034, T042)
- [ ] T044 [US5] Add camera edit functionality in web dashboard to update authentication settings for existing cameras (depends on T025, T040)

**Checkpoint**: At this point, all user stories should be complete - RTSP streams can be secured with authentication

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T045 [P] Add error handling for corrupted video files during upload in src/services/video_library.py
- [ ] T046 [P] Add error handling for video deletion when camera is using it in src/services/video_library.py
- [ ] T047 [P] Add error handling for RTSP connection failures in src/services/rtsp_server.py
- [ ] T048 [P] Add error handling for large video file uploads (progress indication) in web upload interface
- [ ] T049 [P] Add camera start/stop buttons in camera list in web dashboard
- [ ] T050 [P] Add camera delete functionality in web dashboard
- [ ] T051 [P] Add video delete functionality in web dashboard (with check for cameras using video)
- [ ] T052 [P] Update README.md with complete usage instructions and troubleshooting
- [ ] T053 [P] Add logging throughout application for debugging and monitoring
- [ ] T054 Run quickstart.md validation to ensure all setup steps work correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories. Core MVP functionality.
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 services (VideoLibraryService, CameraManagerService) for web interface integration, but web interface can be built independently and integrated later.
- **User Story 3 (P3)**: Can start after US1 - Enhances camera functionality with multi-video support.
- **User Story 4 (P4)**: Can start after US1 - Depends on RTSP streaming from US1, but viewer is independent feature.
- **User Story 5 (P5)**: Can start after US1 - Enhances RTSP server with authentication, can be added independently.

### Within Each User Story

- Models before services
- Services before GUI/endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- Polish phase tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Create Video model in src/models/video.py"
Task: "Create VirtualCamera model in src/models/virtual_camera.py"

# These can be done in parallel as they're different files with no dependencies
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Upload video programmatically
   - Create camera programmatically
   - Connect to RTSP stream with external client (VLC)
   - Verify video plays on repeat
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Web Interface + Auth)
4. Add User Story 3 → Test independently → Deploy/Demo (Multi-video)
5. Add User Story 4 → Test independently → Deploy/Demo (Viewer)
6. Add User Story 5 → Test independently → Deploy/Demo (RTSP Auth)
7. Add Polish → Final release
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (core functionality)
   - Developer B: User Story 2 (Web Interface + Auth) - can start after US1 services are ready
   - Developer C: User Story 3 (Multi-video) - can start after US1
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are not included as they were not requested in the specification
- Focus on working implementation following KISS principle

