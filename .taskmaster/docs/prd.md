<rpg-method>
# Foodie App — Repository Planning Graph (RPG) PRD
# Gemma 4 Hackathon Project | Diamond Challenge Submission

This PRD follows the RPG methodology for Task Master parsing. It captures the full product vision for Foodie — a unified restaurant loyalty and community platform — structured so Task Master can auto-generate a dependency-aware task graph.
</rpg-method>

---

<overview>

## Problem Statement

Loyal restaurant-goers manage loyalty points across a fragmented landscape of individual restaurant apps, physical loyalty cards, and inconsistent programs. There is no single destination that:
- Consolidates reward points across multiple restaurants
- Surfaces **local** food establishments (not just chains) in a discoverable, social way
- Gamifies food exploration to drive traffic to underserved local businesses
- Enables small-scale food entrepreneurs (caterers, home cooks) to reach customers without relying on word-of-mouth

Existing solutions (Yelp, Google Maps, individual restaurant apps) focus on broad discovery or single-brand loyalty. None combine unified points, gamified exploration, community social features, and a local-business-first marketplace into one platform.

## Target Users

**Primary — The Foodie Explorer**
- Age 18–35, active social media user
- Tracks points at 3+ restaurant chains, frustrated by managing multiple apps
- Wants to find new local spots, share food experiences, and earn rewards for exploration

**Secondary — Local Restaurant Owner**
- Small or mid-size restaurant with limited marketing budget
- Wants to attract new customers and promote specific dishes or events
- Currently has no cost-effective way to run targeted promotions

**Tertiary — Independent Food Entrepreneur**
- Catering businesses, home cooks, pop-up vendors
- Relies entirely on word-of-mouth and social media
- Needs a platform to reach paying customers and build a following

**Quaternary — Community & Non-Profit Organizations**
- Food banks, community organizations running food drives
- Want to leverage the platform's user base for participation and donations

## Success Metrics

- 10,000+ active users within 3 months of launch
- 500+ restaurant partners onboarded (loyalty programs integrated)
- Average user earns points from 3+ unique restaurants per month
- 40% of FYP discoveries result in a restaurant visit (tracked via check-in or receipt scan)
- Gemma 4 recommendation accuracy: >75% user satisfaction on FYP suggestions
- 15% of users engage with at least one community event per quarter

</overview>

---

<functional-decomposition>

## Capability Tree

---

### Capability: Unified Points & Loyalty Management
The core value proposition — bringing all restaurant reward programs into one place.

#### Feature: Restaurant Points Aggregator
- **Description**: Connects to and displays points balances from multiple restaurant loyalty programs in a single dashboard
- **Inputs**: User account, linked restaurant loyalty accounts (OAuth or manual entry), restaurant catalog
- **Outputs**: Unified points dashboard showing balance, expiry, and redemption value per restaurant
- **Behavior**: Sync loyalty balances on app open; flag expiring points; calculate cost-per-point-value ratio to show best-deal restaurant

#### Feature: Receipt & Barcode Scanner (OCR Points Upload)
- **Description**: Lets users earn/upload points by scanning a paper receipt or scanning a loyalty barcode at the counter
- **Inputs**: Camera image of receipt or barcode, active restaurant session
- **Outputs**: Points credited to user's account for that restaurant, confirmation screen
- **Behavior**: Use Google Vision API + Gemma 4 for receipt field extraction (restaurant name, total, date, eligible items); validate against restaurant's points formula; post points to linked account

#### Feature: Points Purchase Gateway
- **Description**: Allows users to buy points directly for specific restaurant programs within the app
- **Inputs**: User payment method (Stripe), selected restaurant, point package
- **Outputs**: Points added to restaurant account, transaction record, Foodie revenue capture
- **Behavior**: Display available point packages per restaurant; process payment; update balance in real time

#### Feature: Gamified Exploration Points System
- **Description**: Rewards users with Foodie-native points for exploring new restaurants, cuisines, and dishes
- **Inputs**: User visit history, restaurant database, dish catalog, challenge definitions
- **Outputs**: Foodie points balance, achievement badges, gift card redemption progress
- **Behavior**: Award points for first visit to a new restaurant; bonus multipliers for cuisine diversity; restaurant-configurable dish-level challenges (e.g., "try our new ramen = 2x points"); redeem Foodie points for universal gift cards; Foodie takes a cut on cross-restaurant ordering

#### Feature: Food Pantry & Donation Points
- **Description**: Awards Foodie points for participating in food drives, donations to food banks, or other community food initiatives
- **Inputs**: User participation event record, non-profit partner verification
- **Outputs**: Points credited, participation badge, shareable impact card
- **Behavior**: Partner with verified food non-profits; track participation via QR codes at events; generate shareable impact card for social posting

---

### Capability: Local Discovery & For You Page (FYP)
Surface the right local food spots to the right users — powered by Gemma 4.

#### Feature: Gemma 4 Powered Recommendation Engine (FYP)
- **Description**: Personalized feed of local restaurants and food establishments tailored to each user's taste profile and exploration history
- **Inputs**: User order history, saved places, cuisine preferences, location, time of day, trending local spots
- **Outputs**: Ranked list of restaurant cards with match score, distance, open status, and available points
- **Behavior**: Run Gemma 4 inference on user preference embeddings + restaurant feature vectors; favor under-discovered local establishments; re-rank based on "discovery diversity" to prevent filter bubble; refresh feed on each app open

#### Feature: Interactive Food Map
- **Description**: Full-screen map view showing all nearby food establishments overlaid with user loyalty status
- **Inputs**: Device GPS, restaurant database, user loyalty accounts
- **Outputs**: Map pins color-coded by loyalty status (has points, new, trending); filter by cuisine, distance, open now
- **Behavior**: Cluster pins at zoom-out; tap pin to expand restaurant card; show "you have X points here" badge; highlight establishments running active events or dish challenges

#### Feature: Local Business Spotlight
- **Description**: Dedicated section for small-scale food entrepreneurs (caterers, home cooks, pop-up vendors) to list their offerings
- **Inputs**: Seller profile, menu/dish listings, availability schedule, location
- **Outputs**: Discoverable profile in FYP and map; order/booking inquiry flow
- **Behavior**: Sellers can self-onboard with basic profile; Foodie verifies identity; listings appear in FYP and map with "Local Maker" badge; user can follow seller for availability updates

---

### Capability: Social & Community Layer
Transform eating out from a solo activity into a shared community experience.

#### Feature: Food Post Creator & Monetization
- **Description**: In-app tool to create and share food posts (photos, short videos) tied to a restaurant visit; creators earn from post performance
- **Inputs**: Camera/gallery media, linked restaurant visit, caption, tags
- **Outputs**: Published post on user's Foodie profile and discoverable feed; view/engagement metrics; monetization credit
- **Behavior**: Attach post to a restaurant for geo-discovery; sponsor-boosted posts earn creator a share of ad revenue; viral posts surfaced in FYP of users with matching taste profiles

#### Feature: Restaurant Events Tracker & Hosting
- **Description**: Aggregates and surfaces food events (tastings, competitions, local pop-ups) and enables in-app event hosting
- **Inputs**: Restaurant event listings, community event submissions, user location
- **Outputs**: Personalized event feed, RSVP/ticket flow, event-specific points rewards
- **Behavior**: Restaurants can create events directly in the partner portal; national events (food competitions) curated by Foodie editorial team; RSVP earns bonus Foodie points; post-event recap auto-generated

#### Feature: Community Social Feed
- **Description**: Chronological + algorithmic feed of food posts, events, and restaurant activity from followed users and nearby establishments
- **Inputs**: User social graph, followed restaurants, followed users, location
- **Outputs**: Ranked social feed, notification of new posts/events from followed entities
- **Behavior**: Follow users and restaurants; like, comment, reshare posts; Gemma 4 used to surface trending dishes and spots within the user's community radius

---

### Capability: Restaurant & Partner Portal
Tools for restaurant owners and food businesses to manage their Foodie presence.

#### Feature: Restaurant Onboarding & Profile Management
- **Description**: Self-serve portal for restaurants to join Foodie, set up their loyalty program rules, and manage their profile
- **Inputs**: Business information, loyalty program rules, menu, images, operating hours
- **Outputs**: Live restaurant profile visible to users in map/FYP/events
- **Behavior**: Step-by-step onboarding wizard; loyalty rule builder (points per dollar, bonus items, dish-level challenges); profile edits go live within 24 hours after moderation

#### Feature: Dish-Level Challenge Builder
- **Description**: Allows restaurant partners to configure specific dish challenges that award bonus Foodie points when users order them
- **Inputs**: Menu item selection, point multiplier, challenge duration, eligibility rules
- **Outputs**: Active challenges visible on restaurant profile and FYP; points auto-credited on verified order
- **Behavior**: Restaurants pay Foodie a flat fee to promote a dish via a challenge; Foodie takes a % cut on orders generated through challenge discovery

#### Feature: Partner Analytics Dashboard
- **Description**: Gives restaurant partners visibility into how Foodie is driving traffic, point redemptions, and challenge engagement
- **Inputs**: Restaurant ID, date range, event IDs
- **Outputs**: Dashboard with visit attribution, point redemptions, post mentions, challenge completion rates, revenue from Foodie channel
- **Behavior**: Update data daily; exportable CSV; highlight top-performing dishes and posts

---

### Capability: Payments & Monetization Infrastructure
The revenue engine powering Foodie's sustainability.

#### Feature: In-App Payments (Stripe Integration)
- **Description**: Handles all monetary transactions within Foodie — point purchases, food ordering commissions, event tickets, creator payouts
- **Inputs**: User payment method, transaction type, amount
- **Outputs**: Confirmed payment, updated balances, receipt
- **Behavior**: PCI-compliant via Stripe; support card, Apple Pay, Google Pay; creator payouts via Stripe Connect; Foodie takes configurable % cut on cross-restaurant orders

#### Feature: Gift Card Redemption System
- **Description**: Allows users to convert accumulated Foodie gamification points into universal gift cards
- **Inputs**: Foodie points balance, selected gift card denomination/brand
- **Outputs**: Issued gift card code, deducted points balance
- **Behavior**: Partner with gift card aggregator API (e.g., Tango Card); threshold-based redemption (minimum 1000 Foodie points); Foodie buys gift cards at wholesale and captures the spread as margin

</functional-decomposition>

---

<structural-decomposition>

## Repository Structure

```
foodie/
├── apps/
│   ├── mobile/                    # React Native app (iOS + Android)
│   │   ├── src/
│   │   │   ├── screens/           # Screen-level components
│   │   │   ├── components/        # Shared UI components
│   │   │   ├── navigation/        # React Navigation setup
│   │   │   ├── store/             # Redux Toolkit state management
│   │   │   ├── hooks/             # Custom React hooks
│   │   │   └── utils/             # Client-side utilities
│   │   └── assets/                # Images, fonts, icons
│   └── partner-portal/            # React web app for restaurant partners
│       └── src/
│           ├── pages/
│           ├── components/
│           └── api/
├── packages/
│   ├── api-client/                # Shared typed API client (used by mobile + portal)
│   └── shared-types/              # Shared TypeScript types
├── services/
│   ├── api-gateway/               # Node.js/Express main API
│   │   ├── src/
│   │   │   ├── routes/            # Express route handlers
│   │   │   ├── middleware/        # Auth, rate limiting, logging
│   │   │   ├── controllers/       # Business logic layer
│   │   │   └── validators/        # Zod schema validation
│   ├── auth-service/              # Authentication microservice (JWT + OAuth)
│   ├── points-service/            # Loyalty points engine
│   │   ├── src/
│   │   │   ├── aggregator/        # Multi-restaurant points sync
│   │   │   ├── scanner/           # OCR receipt processing pipeline
│   │   │   ├── gamification/      # Foodie-native points + challenges
│   │   │   └── gift-cards/        # Gift card redemption
│   ├── recommendations-service/   # Gemma 4 FYP inference service (Python/FastAPI)
│   │   ├── src/
│   │   │   ├── embeddings/        # User + restaurant feature embeddings
│   │   │   ├── inference/         # Gemma 4 model calls
│   │   │   └── ranking/           # Post-inference re-ranking
│   ├── social-service/            # Posts, comments, follows, feed
│   ├── events-service/            # Restaurant events + community events
│   ├── payments-service/          # Stripe integration
│   └── notifications-service/     # Push notifications (FCM/APNs)
├── infrastructure/
│   ├── terraform/                 # Cloud infrastructure (AWS)
│   ├── docker/                    # Docker compose for local dev
│   └── k8s/                       # Kubernetes manifests (production)
├── .taskmaster/
│   ├── docs/prd.md               # This file
│   └── tasks/                     # Auto-generated by Task Master
└── docs/
    └── architecture.md
```

## Module Definitions

### Module: shared-types
- **Maps to capability**: All capabilities (foundational)
- **Responsibility**: Single source of truth for TypeScript interfaces and enums shared across all services and apps
- **Exports**: `User`, `Restaurant`, `LoyaltyAccount`, `FoodiePoints`, `Post`, `Event`, `Order`, `Challenge`, `GiftCard`, `Notification`

### Module: auth-service
- **Maps to capability**: User authentication across all capabilities
- **Responsibility**: JWT issuance/validation, OAuth flows for third-party restaurant loyalty accounts, social login (Google, Apple)
- **Exports**: `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/oauth/:provider`

### Module: points-service/aggregator
- **Maps to capability**: Unified Points & Loyalty Management
- **Responsibility**: Fetches and syncs loyalty balances from partner restaurant APIs/scrapers
- **Exports**: `syncRestaurantPoints(userId, restaurantId)`, `getPointsDashboard(userId)`

### Module: points-service/scanner
- **Maps to capability**: Receipt & Barcode Scanner
- **Responsibility**: Processes camera images via Google Vision API + Gemma 4 to extract receipt fields and credit points
- **Exports**: `processReceiptImage(imageBuffer, restaurantId)`, `processBarcodeCapture(barcode, restaurantId)`

### Module: points-service/gamification
- **Maps to capability**: Gamified Exploration Points System
- **Responsibility**: Manages Foodie-native points, challenges, badges, leaderboards, and gift card progress
- **Exports**: `awardExplorationPoints(userId, event)`, `getActiveChallenges(userId, location)`, `redeemForGiftCard(userId, denomination)`

### Module: recommendations-service
- **Maps to capability**: Gemma 4 Powered FYP
- **Responsibility**: Builds user taste embeddings, runs Gemma 4 inference, returns ranked restaurant list
- **Exports**: `GET /recommendations/fyp?userId=&lat=&lng=`, `GET /recommendations/map-boost?restaurantIds=`

### Module: social-service
- **Maps to capability**: Social & Community Layer
- **Responsibility**: Post creation/storage, social graph (follows), feed assembly, comments, likes, creator payout tracking
- **Exports**: `createPost`, `getFeed`, `followUser`, `followRestaurant`, `getCreatorMetrics`

### Module: events-service
- **Maps to capability**: Restaurant Events Tracker & Hosting
- **Responsibility**: Event CRUD, RSVP management, event-based points awards, event discovery by location
- **Exports**: `createEvent`, `getEventsFeed`, `rsvpEvent`, `getRestaurantEvents`

### Module: payments-service
- **Maps to capability**: Payments & Monetization Infrastructure
- **Responsibility**: Stripe payment processing, Stripe Connect for creator payouts, gift card API integration
- **Exports**: `createPaymentIntent`, `confirmOrder`, `payoutCreator`, `redeemGiftCard`

### Module: partner-portal
- **Maps to capability**: Restaurant & Partner Portal
- **Responsibility**: React web app for restaurant partner self-service — onboarding, loyalty rule config, challenge builder, analytics dashboard
- **Exports**: Web application (deployed separately)

</structural-decomposition>

---

<dependency-graph>

## Dependency Chain

### Foundation Layer (Phase 0)
No dependencies — these are built first.

- **shared-types**: TypeScript interfaces for all data models; zero external deps
- **infrastructure/docker**: Local dev environment (PostgreSQL, Redis, RabbitMQ); prerequisite for all services
- **auth-service**: JWT + OAuth auth foundation; all other services depend on validated tokens

### Data Layer (Phase 1)
Depends on Phase 0.

- **api-gateway**: Depends on [auth-service, shared-types] — Express server, routing skeleton, middleware (auth, logging, rate limiting)
- **points-service/aggregator**: Depends on [auth-service, shared-types] — restaurant loyalty sync engine
- **payments-service**: Depends on [auth-service, shared-types] — Stripe foundation (payment intents, webhooks)

### Core Intelligence Layer (Phase 2)
Depends on Phase 1.

- **points-service/scanner**: Depends on [points-service/aggregator, payments-service] — OCR pipeline needs aggregator to know which restaurant to credit
- **points-service/gamification**: Depends on [points-service/aggregator, payments-service] — challenge rewards credit via aggregator; gift card redemption via payments
- **recommendations-service**: Depends on [api-gateway, points-service/aggregator] — needs user loyalty data and restaurant catalog to build embeddings

### Social & Events Layer (Phase 3)
Depends on Phase 2.

- **social-service**: Depends on [auth-service, recommendations-service, payments-service] — feed powered by recommendations; creator monetization via payments
- **events-service**: Depends on [auth-service, points-service/gamification, payments-service] — event RSVP awards gamification points; ticketed events go through payments

### Presentation Layer (Phase 4)
Depends on Phase 3.

- **apps/mobile**: Depends on [all services via api-gateway] — React Native app, connects to all backend services
- **apps/partner-portal**: Depends on [api-gateway, points-service/aggregator, events-service] — restaurant partner web dashboard

### Scale & Optimization Layer (Phase 5)
Depends on Phase 4 (post-MVP).

- **notifications-service**: Depends on [social-service, events-service, points-service/gamification] — push alerts for social activity, event reminders, expiring points
- **infrastructure/k8s**: Depends on [all services] — production Kubernetes deployment, load balancing, auto-scaling

</dependency-graph>

---

<implementation-roadmap>

## Development Phases

---

### Phase 0: Foundation
**Goal**: Establish shared types, local dev environment, and authentication so all other services have a stable base to build on.

**Entry Criteria**: Clean repository, Node.js 20+ and Python 3.11+ installed, AWS account provisioned.

**Tasks**:
- [ ] Initialize monorepo structure with Turborepo + pnpm workspaces (depends on: none)
  - Acceptance criteria: `pnpm install` succeeds; `turbo build` builds all packages with zero errors
  - Test strategy: CI build passes
- [ ] Define shared TypeScript types package — `User`, `Restaurant`, `LoyaltyAccount`, `FoodiePoints`, `Post`, `Event`, `Challenge`, `GiftCard` (depends on: monorepo init)
  - Acceptance criteria: All core domain types exported and importable from any workspace package
  - Test strategy: TypeScript type-check passes with `tsc --noEmit`
- [ ] Spin up local dev environment with Docker Compose: PostgreSQL, Redis, RabbitMQ (depends on: monorepo init)
  - Acceptance criteria: `docker compose up` starts all services; health checks pass
  - Test strategy: Manual connection verification from each service
- [ ] Build auth-service: user registration, JWT login, refresh token, Google/Apple OAuth (depends on: shared-types, docker env)
  - Acceptance criteria: Register → login → refresh flow works end-to-end; OAuth redirect completes
  - Test strategy: Unit tests for token issuance/validation; integration test for full auth flow

**Exit Criteria**: Developer can register a user, obtain a JWT, and make an authenticated request against a stub endpoint.

**Delivers**: Developer environment is fully operational; authentication backbone is live.

---

### Phase 1: Core API & Payments Foundation
**Goal**: Stand up the API gateway, restaurant data layer, and payment processing so Phase 2 services have a surface to call.

**Entry Criteria**: Phase 0 complete; at least 2 restaurant partner APIs identified for integration.

**Tasks**:
- [ ] Build api-gateway: Express server, auth middleware, route registration, error handling, rate limiting (depends on: auth-service)
  - Acceptance criteria: All downstream service routes proxied correctly; unauthenticated requests return 401
  - Test strategy: Integration tests for auth middleware; smoke tests for route availability
- [ ] Build restaurant catalog service: store restaurant profiles, loyalty program rules, menus, operating hours in PostgreSQL (depends on: api-gateway, shared-types)
  - Acceptance criteria: CRUD operations for restaurants; seed 10+ sample restaurants
  - Test strategy: Unit tests for CRUD; integration test verifying DB persistence
- [ ] Build points-service/aggregator: sync loyalty balances for 2+ restaurant partners via API/scraper (depends on: restaurant-catalog, auth-service)
  - Acceptance criteria: User can link a Chick-fil-A or Starbucks account and see their points balance in the app
  - Test strategy: Mock API tests for each integration; live sync test against at least 1 partner
- [ ] Build payments-service: Stripe payment intents, webhook handler, Stripe Connect onboarding for creator payouts (depends on: auth-service, shared-types)
  - Acceptance criteria: Test payment flows through Stripe dashboard; webhook events processed correctly
  - Test strategy: Stripe CLI test event replay; unit tests for webhook handler logic

**Exit Criteria**: User can link a loyalty account, see their balance, and make a test purchase.

**Delivers**: The core economic loop (loyalty data in, payments out) is functional.

---

### Phase 2: Scanner, Gamification & Recommendations
**Goal**: Deliver the two killer features — receipt scanning and the Gemma 4 FYP — so the app is demonstrably differentiated.

**Entry Criteria**: Phase 1 complete; Google Vision API key provisioned; Google AI Studio / Vertex AI access for Gemma 4.

**Tasks**:
- [ ] Build receipt OCR pipeline: Google Vision API extracts text, Gemma 4 parses restaurant name, total, eligible items, dates (depends on: points-service/aggregator)
  - Acceptance criteria: 85%+ accuracy on a test set of 50 real receipts across 10 restaurant types
  - Test strategy: Offline accuracy test against labeled receipt dataset; unit tests for field extraction
- [ ] Build barcode scanner: decode loyalty QR/barcodes at POS; post points to linked account (depends on: points-service/aggregator)
  - Acceptance criteria: Successfully scan and credit points for 3 partner restaurants' loyalty barcodes
  - Test strategy: Integration test with physical barcodes; fallback handling for unrecognized codes
- [ ] Build gamification engine: exploration points logic, challenge evaluation, badge award system, leaderboard, gift card redemption threshold tracker (depends on: points-service/aggregator, payments-service)
  - Acceptance criteria: User earns Foodie points for visiting a new restaurant; challenge completion auto-awards bonus points; 1000 points unlocks gift card redemption flow
  - Test strategy: Unit tests for each points rule; integration test for full challenge → redemption flow
- [ ] Build recommendations-service with Gemma 4: user embedding builder, Gemma 4 ranking call, diversity re-ranker, REST endpoint (depends on: restaurant-catalog, points-service/aggregator)
  - Acceptance criteria: FYP endpoint returns 20 ranked restaurants in <500ms; at least 60% are local (non-chain) establishments; Gemma 4 prompt tuned for food preference reasoning
  - Test strategy: A/B latency test; manual relevance review on 5 test user profiles

**Exit Criteria**: Demo-able: user scans a receipt, earns Foodie points, and sees a personalized restaurant feed.

**Delivers**: The hackathon-ready core of the app is functional — points, scanning, and Gemma 4 FYP all working end-to-end.

---

### Phase 3: Social, Events & Partner Portal
**Goal**: Add the community layer and give restaurant partners tools to manage their presence.

**Entry Criteria**: Phase 2 complete; at least 3 real restaurant partners signed up.

**Tasks**:
- [ ] Build social-service: post creation (photo/video), social graph (follow/unfollow), feed assembly, likes, comments (depends on: auth-service, recommendations-service)
  - Acceptance criteria: User can post a food photo tied to a restaurant, follow another user, and see their posts in the feed
  - Test strategy: Unit tests for feed ranking; integration tests for post → feed propagation
- [ ] Build creator monetization: track post views, calculate creator earnings, trigger Stripe Connect payout at threshold (depends on: social-service, payments-service)
  - Acceptance criteria: Creator payout triggers correctly when view threshold is met; payout appears in Stripe dashboard
  - Test strategy: Mock view events to trigger payout; unit tests for earnings calculation
- [ ] Build events-service: event CRUD, RSVP flow, location-based event discovery, event-based points awards (depends on: auth-service, points-service/gamification, payments-service)
  - Acceptance criteria: Restaurant can create an event; user RSVPs and receives confirmation + bonus points; event appears on map
  - Test strategy: End-to-end test for event creation → RSVP → points award flow
- [ ] Build partner portal frontend: onboarding wizard, loyalty rule builder, challenge creator, analytics dashboard (depends on: api-gateway, restaurant-catalog, events-service)
  - Acceptance criteria: Restaurant owner completes onboarding in <10 min; loyalty rules reflect in user-facing app within 1 hour
  - Test strategy: UAT walkthrough with 1 real restaurant partner

**Exit Criteria**: Restaurant partner is onboarded, has created at least one challenge and one event, and analytics are showing activity.

**Delivers**: Full social community layer + partner self-service is live.

---

### Phase 4: Mobile App (Full UI)
**Goal**: Ship the polished React Native app integrating all backend capabilities.

**Entry Criteria**: Phases 1–3 complete; all API endpoints documented via Swagger.

**Tasks**:
- [ ] Build authentication screens: onboarding, registration, login, social auth (depends on: auth-service API)
- [ ] Build points dashboard screen: unified loyalty balances, expiry alerts, cost-per-point ratio display (depends on: points-service/aggregator API)
- [ ] Build receipt/barcode scanner screen: camera integration, scan feedback, points confirmation (depends on: scanner API)
- [ ] Build interactive map screen: MapBox/Google Maps integration, restaurant pins with loyalty overlay, filters (depends on: restaurant-catalog, recommendations-service API)
- [ ] Build FYP / discovery feed: Gemma 4 recommendations feed, local business spotlight cards (depends on: recommendations-service API)
- [ ] Build social feed & post creator: food post upload, feed scroll, like/comment, follow (depends on: social-service API)
- [ ] Build events screen: event cards, RSVP flow, national vs local toggle (depends on: events-service API)
- [ ] Build gamification hub: Foodie points balance, active challenges, leaderboard, gift card redemption (depends on: points-service/gamification API)
- [ ] Build payments screen: point purchase, transaction history, creator earnings (depends on: payments-service API)
- [ ] Build notifications: push notifications for social activity, expiring points, event reminders (depends on: notifications-service)

**Exit Criteria**: Full end-to-end user journey works on both iOS and Android simulators; TestFlight beta build submitted.

**Delivers**: A shippable mobile app ready for user testing and hackathon demo.

---

### Phase 5: Scale & Production Hardening (Post-MVP)
**Goal**: Prepare the platform for real user load and maintainability.

**Entry Criteria**: Phase 4 complete; beta testing feedback incorporated.

**Tasks**:
- [ ] Migrate to Kubernetes (k8s) on AWS EKS; set up auto-scaling, load balancers, managed RDS (depends on: all services)
- [ ] Build notifications-service: FCM + APNs push integration, notification preference management (depends on: social-service, events-service, points-service/gamification)
- [ ] Integrate CDN (CloudFront) for media assets (post images, videos) (depends on: social-service)
- [ ] Implement analytics pipeline: event tracking → S3 → Redshift → partner analytics dashboard (depends on: all services)
- [ ] App Store & Google Play submission: metadata, screenshots, review compliance (depends on: Phase 4)

**Exit Criteria**: Platform handles 1,000 concurrent users without degradation; apps approved in both stores.

**Delivers**: Production-ready platform ready for public launch.

</implementation-roadmap>

---

<test-strategy>

## Test Pyramid

```
        /\
       /E2E\       ← 10% (Full user journeys: scan receipt → earn points → redeem gift card)
      /------\
     /Integration\ ← 30% (Service-to-service calls, DB persistence, Stripe webhooks, Gemma 4 API)
    /------------\
   /  Unit Tests  \ ← 60% (Points calculation, gamification rules, OCR field parsing, embedding logic)
  /----------------\
```

## Coverage Requirements
- Line coverage: 80% minimum (points-service and payments-service: 90%)
- Branch coverage: 75% minimum
- Function coverage: 85% minimum
- Statement coverage: 80% minimum

## Critical Test Scenarios

### points-service/scanner (OCR Pipeline)
**Happy path**:
- Valid Starbucks receipt image → extracts restaurant, total, date → credits correct points
- Expected: Points credited within 3 seconds; user sees confirmation

**Edge cases**:
- Crumpled/low-light receipt → Gemma 4 still parses key fields with >80% accuracy
- Duplicate receipt submission → idempotency key prevents double-crediting
- Receipt from non-partner restaurant → graceful "restaurant not in network" message

**Error cases**:
- Google Vision API timeout → retry with exponential backoff; fallback to manual entry prompt
- Points sync failure → transaction rolled back; no partial credit

### recommendations-service (Gemma 4 FYP)
**Happy path**:
- New user (cold start) → returns geographically diverse local spots as seed recommendations
- Returning user with history → FYP skews toward unexplored cuisine types

**Edge cases**:
- User location in area with <5 restaurants → gracefully expands radius
- Gemma 4 API rate limit hit → serve cached recommendations with staleness indicator

**Error cases**:
- Gemma 4 inference failure → fallback to collaborative filtering (no model); log for alerting

### payments-service (Stripe)
**Happy path**:
- Point purchase → Stripe payment intent created → confirmed → balance updated → receipt sent

**Edge cases**:
- Stripe webhook arrives out of order → idempotent handler processes correctly regardless of order
- Creator payout below Stripe minimum → accumulate; pay out when threshold reached

**Error cases**:
- Payment declined → user shown actionable error; no points credited
- Stripe outage → queue transaction for retry; user notified of delay

### gamification engine
**Happy path**:
- User visits new restaurant → exploration points awarded → progress toward gift card updated
- Restaurant dish challenge active → user scans receipt for that dish → 2x points applied

**Edge cases**:
- User tries to game system (multiple check-ins same restaurant in 1 day) → daily cap enforced
- Challenge expires mid-day → points awarded for receipts before expiry only

## Test Generation Guidelines
- All points arithmetic should have property-based tests (fast-check) to catch edge-case rounding errors
- Gemma 4 prompt tests should use golden-file comparison (saved expected outputs) to detect prompt regressions
- Stripe tests must use `stripe-mock` for unit/integration; never hit real Stripe in CI
- OCR tests require a fixture library of labeled receipt images (build this in Phase 2)
- Use `supertest` for API integration tests; `jest` for unit tests; `detox` for mobile E2E

</test-strategy>

---

<architecture>

## System Components

```
Mobile App (React Native)
        │
        ▼
   API Gateway (Express/Node.js)
   ├── Auth Middleware (JWT)
   ├── Rate Limiter (Redis)
   └── Service Router
        │
   ┌────┼─────────────────────────────────────┐
   ▼    ▼              ▼              ▼        ▼
Points  Social     Events        Payments  Recommendations
Service Service    Service       Service   Service (Python)
   │                                           │
   ├── Aggregator                         Gemma 4 API
   ├── Scanner                           (Google Vertex AI)
   └── Gamification
        │
   Google Vision API
   (OCR)
        │
   PostgreSQL (primary DB)
   Redis (cache + sessions)
   RabbitMQ (async events)
   S3 (media storage)
```

## Data Models

**User**: `id`, `email`, `displayName`, `avatar`, `location`, `tasteProfile (JSON)`, `foodiePoints`, `creatorEarnings`, `linkedLoyaltyAccounts[]`

**Restaurant**: `id`, `name`, `cuisineType`, `address`, `coordinates`, `loyaltyProgram (JSON)`, `activeChallenges[]`, `isLocalBusiness (bool)`, `isPartner (bool)`

**LoyaltyAccount**: `id`, `userId`, `restaurantId`, `externalAccountId`, `pointsBalance`, `lastSynced`, `expiresAt`

**FoodiePointsTransaction**: `id`, `userId`, `amount`, `type (exploration|challenge|donation|purchase)`, `restaurantId`, `timestamp`, `metadata (JSON)`

**Post**: `id`, `authorId`, `restaurantId`, `mediaUrls[]`, `caption`, `viewCount`, `likes`, `comments[]`, `earningsAccrued`

**Challenge**: `id`, `restaurantId`, `dishName`, `pointMultiplier`, `startDate`, `endDate`, `completionCount`

**Event**: `id`, `restaurantId`, `title`, `description`, `eventType (local|national)`, `date`, `location`, `rsvpCount`, `pointsReward`

**GiftCardRedemption**: `id`, `userId`, `pointsSpent`, `giftCardCode`, `denomination`, `brand`, `redeemedAt`

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Mobile | React Native + Expo | Cross-platform iOS/Android; large ecosystem |
| Backend API | Node.js + Express + TypeScript | Team familiarity; strong async I/O for high concurrency |
| Recommendations | Python + FastAPI | Python-first ML ecosystem; FastAPI async performance |
| AI Model | Google Gemma 4 (via Vertex AI) | Hackathon requirement; strong reasoning for preference inference |
| OCR | Google Vision API | Best-in-class receipt field extraction accuracy |
| Database | PostgreSQL + Prisma ORM | ACID compliance for financial transactions; Prisma type safety |
| Cache | Redis | Session storage, rate limiting, FYP cache |
| Queue | RabbitMQ | Async points sync, notification dispatch, payout processing |
| Payments | Stripe + Stripe Connect | Industry standard; Connect handles marketplace payouts |
| Media Storage | AWS S3 + CloudFront CDN | Cost-effective; CDN for global low-latency media delivery |
| Auth | JWT + Passport.js | Stateless auth; easy OAuth integration |
| Project Management | Task Master AI | Dependency-aware task graph; LLM coordination for agile workflow |

**Decision: Gemma 4 for FYP Recommendations**
- **Rationale**: Hackathon requirement; Gemma 4's large context window and strong reasoning capability allow multi-factor preference inference beyond simple collaborative filtering
- **Trade-offs**: Inference latency (~200–400ms); API cost per request
- **Mitigation**: Cache FYP results per user for 4 hours; only re-rank on explicit refresh or significant new activity

**Decision: Monorepo (Turborepo)**
- **Rationale**: Single source of truth for types; unified CI; easy cross-package refactoring
- **Trade-offs**: Larger initial setup; more complex CI pipeline
- **Alternatives considered**: Separate repos per service — rejected due to type drift and version management overhead

</architecture>

---

<risks>

## Technical Risks

**Risk**: Restaurant loyalty API integrations are undocumented or rate-limited
- **Impact**: High — without real integrations, the core points aggregation doesn't work
- **Likelihood**: High — most chains don't publish public loyalty APIs
- **Mitigation**: Build scraper-based fallback using authenticated session simulation (Playwright); partner directly with 3–5 restaurants that agree to API access for the hackathon
- **Fallback**: Manual points entry as a user-facing fallback; pitch the aggregation model to investors even without full automation

**Risk**: Gemma 4 inference latency exceeds acceptable FYP load time (>1s)
- **Impact**: Medium — poor UX if FYP takes too long to load
- **Likelihood**: Medium — model inference is inherently slow without hardware acceleration
- **Mitigation**: Pre-compute and cache FYP rankings every 4 hours per user; serve cached results instantly; refresh asynchronously in background
- **Fallback**: Fall back to collaborative filtering (no Gemma 4) if inference p95 > 800ms

**Risk**: OCR receipt accuracy too low for reliable points crediting
- **Impact**: High — false credits or missed points erode user trust
- **Likelihood**: Medium — receipt quality varies wildly in the real world
- **Mitigation**: Two-pass approach (Vision API → Gemma 4 structured extraction); human review queue for low-confidence parses; user can manually correct extracted fields
- **Fallback**: Manual points entry with photo upload for audit trail

## Dependency Risks

**Risk**: Stripe Connect approval takes longer than expected (KYC for marketplace)
- **Impact**: Medium — creator monetization and point purchases blocked
- **Mitigation**: Apply for Stripe Connect immediately at project start; build UI with "coming soon" state for monetization features during review

**Risk**: Google Vertex AI / Gemma 4 quota limits during hackathon demo
- **Impact**: High — live demo fails
- **Mitigation**: Pre-warm model endpoint; cache all demo user FYP results before the presentation; have a static fallback demo mode ready

## Scope Risks

**Risk**: Social layer (posts, feed, creator monetization) adds 3–4 weeks of scope
- **Impact**: Medium — hackathon timeline may not accommodate full social layer
- **Mitigation**: MVP social layer = post creation + basic feed only; creator monetization and advanced social graph deferred to Phase 5
- **Boundary**: For Diamond Challenge submission, prioritize: (1) points aggregation, (2) receipt scanning, (3) Gemma 4 FYP, (4) map view. Social is a bonus.

**Risk**: Local food entrepreneur marketplace requires significant trust & safety work (fraud, identity verification)
- **Impact**: Low for MVP — feature is valuable but not critical for hackathon
- **Mitigation**: Launch with curated invite-only seller list; open marketplace only after fraud controls are in place

</risks>

---

<appendix>

## References
- Diamond Challenge competition guidelines: https://diamondchallenge.org/competition/
- Google Gemma 4 model documentation: https://ai.google.dev/gemma
- Google Vision API (receipt OCR): https://cloud.google.com/vision/docs/receipt-ocr
- Stripe Connect for marketplaces: https://stripe.com/docs/connect
- React Native documentation: https://reactnative.dev/docs/getting-started
- Task Master AI: https://github.com/eyaltoledano/claude-task-master

## Glossary
- **Foodie Points**: The platform's native gamification currency, separate from individual restaurant loyalty points
- **FYP (For You Page)**: The personalized restaurant discovery feed powered by Gemma 4
- **Dish Challenge**: A time-limited, restaurant-configured bonus points event tied to ordering a specific menu item
- **Local Business Spotlight**: The marketplace section for independent food entrepreneurs not on major platforms
- **RPG (Repository Planning Graph)**: The PRD methodology used to generate dependency-aware Task Master tasks
- **Partner Portal**: The web dashboard for restaurant owners to manage their Foodie presence

## Open Questions
1. Which restaurant loyalty APIs are accessible for hackathon integration? (Starbucks, Chick-fil-A, Panera all have documented OAuth flows)
2. What is the Google Vertex AI quota for Gemma 4 inference during the hackathon window?
3. Will Diamond Challenge judges evaluate a live demo or a recorded pitch?
4. Should the gift card redemption use Tango Card API or a simpler mock for MVP?
5. What minimum number of restaurant partners can be onboarded before the competition deadline?

</appendix>
