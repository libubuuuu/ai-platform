# Enterprise Social Content Platform Blueprint

## Boundary

This is a compliant content operations platform.

Not included:
- IP rotation or IP isolation
- Anti-detection or bypassing platform risk controls
- Automated spam or covert mass-commenting
- Unauthorized account access

All publishing must use official APIs or authorized integrations.

## Main Modules

1. Platform selector and content radar
   - Domestic or overseas platform filters
   - Content type labels: text, image, video
   - Source attribution and trend analysis

2. Cart and remix workspace
   - Select multiple items
   - Remove items from cart
   - Merge or rewrite selected drafts
   - Preserve image or video references when present

3. Canvas for image similarity
   - Drag an image into the canvas
   - Extract prompts
   - Generate similar images
   - Reuse generated results

4. Publishing center
   - Bind authorized accounts
   - Push to drafts or scheduled queues
   - Choose platform and account
   - Add approval and audit logs

5. AI comment assistant
   - Generate comment suggestions
   - Support multi-target analysis
   - Require human confirmation before posting

## Enterprise Stack

- Frontend: React or Next.js with TypeScript
- Backend: FastAPI
- Database: PostgreSQL
- Cache and jobs: Redis
- Storage: S3 or MinIO
- Search: OpenSearch if needed

## Security

- RBAC and MFA
- Secret vault for tokens
- Encryption in transit and at rest
- Full audit logs
- Rate limits and approval workflows

## Fit With This Repo

The current repo is a video/audio sync analyzer, so it needs a full refactor to become this product.
