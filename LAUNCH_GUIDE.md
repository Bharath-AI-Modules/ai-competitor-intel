# Pilot and launch guide

## Who to sell to and what to promise

Start with independent marketing agencies and freelance strategists who repeatedly research competitors for client positioning, landing-page rewrites, or campaign briefs. Interview a narrow segment first—for example, agencies with a few active B2B SaaS clients—rather than marketing this as useful to every business.

Position the product as **faster, repeatable competitor messaging research**: compare up to five public landing pages, see the positioning and offer patterns with supporting page excerpts, and revisit saved snapshots to discuss what changed. Sell analyst time saved and a clearer client conversation, not “AI accuracy,” guaranteed revenue, or continuous monitoring.

The current app is suitable for supervised pilots and local research. It does not yet provide scheduled crawls, notifications, user accounts, team workspaces, billing, customer support workflows, durable hosted storage, or a production service-level commitment. Do not list those as existing features.

## Pricing hypotheses to test

These are experiments, not established market prices or earnings forecasts:

| Offer to test | Hypothesis | Pilot boundaries |
|---|---|---|
| Paid research pilot: $99 for two weeks | An agency may pay for setup and a few analyst-assisted reports before subscribing | One client, up to five competitor URLs, two comparison sessions, feedback call |
| Solo: $49/month | A solo strategist may pay for a recurring monthly research workflow | One user, a small number of manually run reports, customer supplies their own Gemini key |
| Agency: $149/month | A small agency may pay for shared client projects and repeatable reporting | Only sell after team access, usage limits, and secure persistence exist; for now, offer a clearly scoped manual service instead |

Ask at least 5–10 target buyers about their current research process, frequency, time cost, and budget before choosing a price. Offer a real paid pilot with a written scope, cancellation/refund terms, and invoice/receipt. Track pilot-to-paid conversion, weekly use, time saved, support hours, and gross costs (including Gemini usage). If the reports do not lead to repeat use, revise the workflow before adding a subscription.

For recurring revenue now, the honest MVP path is a **human-led monthly competitor briefing**: agree a client URL set, run the comparisons manually on an agreed cadence, verify evidence, and deliver a branded report plus analyst interpretation. Charge a fixed monthly retainer only after agreeing the deliverables and time budget. Do not imply the app itself watches sites between runs. Productize automation only after customers validate that they will pay for it.

## Find the first paying customers

1. Identify 20–30 small agencies or independent strategists serving one niche. Use your own professional network, local business groups, agency directories, LinkedIn, and relevant founder/marketing communities; follow each community's outreach rules.
2. Send a short, personal note asking about their competitor-research workflow. Show a sample report using public sites, clearly labelled as a demo, and ask whether the evidence and comparison would help an upcoming client project.
3. Offer a bounded paid pilot rather than a free indefinite trial. Define the client, competitor set, number of sessions, turnaround, deliverable, price, and what is not included.
4. Request permission before using a customer's name, logo, quotes, or report as a case study. Remove client-sensitive details from demos. Do not make performance claims without evidence.
5. Review usage and buyer feedback after each pilot; change the workflow or pricing only when the evidence supports it.

## Public listing options

### GitHub

- Decide whether the repository should be public. A public source repository is inspectable and is not by itself a paid SaaS listing. Review the source for secrets, add an appropriate open-source license only if you intend to grant those rights, and ensure the README describes limitations and data handling.
- Improve the repository landing page with a clear, truthful one-sentence value proposition, setup instructions, a demo screenshot made from public/example data, support/contact details, and a link to a hosted demo if one exists.
- Publish only after reviewing GitHub terms, any chosen license, branding/trademark use, and the repository contents. Do not claim the tool is endorsed by Google or Streamlit.

### Streamlit Community Cloud

- Create a Streamlit account and connect the GitHub account/repository. Choose the repository, branch, and `app.py` as the entry point in the deployment flow.
- Confirm the hosting plan's repository visibility, resource, sleep, and usage constraints before relying on it for customers. A free public demo is for validation, not a production uptime or storage guarantee.
- Install from `requirements.txt`. Configure any app secrets through the provider's secret settings; never commit `.streamlit/secrets.toml` or API keys.
- **Do not deploy an owner-funded `GEMINI_API_KEY` on an unauthenticated public app.** Anyone who can reach the app may trigger calls and spend against that key. Keep a hosted pilot private/restricted, require users to enter their own keys, or add authentication, quotas, abuse controls, and billing before considering a shared key.
- Local SQLite files on a hosted container are not durable backups. For paid use, add managed persistent storage and a tested backup/retention policy before promising saved history.

### Product directories and marketplaces

After a reliable hosted demo and customer-ready support/privacy information exist, consider Product Hunt for a launch announcement, and SaaSHub or AlternativeTo for discovery. These are distribution experiments, not guaranteed sources of traffic or customers; check each site's current submission rules and fees. Do not submit to a paid software marketplace until account, support, refund, privacy, uptime, and billing responsibilities are ready. This repository does not currently expose a hosted API suitable for API marketplaces.

## Deployment and provider setup

For a private/local pilot:

1. Install Python and dependencies as in the README, create a Gemini API key in Google AI Studio, and set `GEMINI_API_KEY` locally or enter it for each session.
2. Run `streamlit run app.py`, compare public pages, and check every AI claim against its quoted source.
3. Back up the SQLite database if you need to retain pilot reports. Restrict file and machine access.

For a restricted hosted demo:

1. Create/verify GitHub and Streamlit Community Cloud accounts and choose the repository visibility and hosting plan.
2. Deploy `app.py` from the intended branch and verify logs, limits, and secret handling.
3. Keep it private or gated while using an owner-managed Gemini key. Review Google's current Gemini API terms, pricing, rate limits, and data handling; configure budget/rate controls where available.
4. Test URL fetching, errors, reports, and downloads from the deployed instance. Explain that a page's text is sent to Google for analysis and is stored in local app storage only as long as that hosting storage survives.

Before publicly selling a hosted subscription, arrange sign-in and authorization, per-customer usage limits, durable database/storage, scheduled execution and failure notifications (if advertising monitoring), payment processing, customer support, backups, privacy/retention controls, and an incident response path. A payment provider such as Stripe requires an eligible account, identity/business and bank details, and approval in supported regions; configure products, taxes, invoices, cancellation/refunds, and webhooks yourself. Ask an accountant or qualified adviser about local tax, privacy, consumer-protection, and business-registration obligations. Do not collect payments until these policies and operational responsibilities are understood.

## Human decisions and setup still required

- Choose the initial niche and interview real buyers; validate demand and prices rather than treating the hypotheses above as promises.
- Select a public/private repository policy, license, support contact, product name/trademark clearance, and hosting plan.
- Create and protect provider accounts/keys and decide whether a demo uses customers' keys or has controlled server-side quotas.
- Write customer-facing privacy, terms, data-retention, cancellation/refund, and support policies appropriate to your jurisdiction and product.
- Set up any business registration, tax, payment processor, domain, custom branding, and customer communications.
- Decide what counts as a tracked change and how frequently to check websites before selling automated monitoring.

No listing, account, business registration, payment integration, deployment, customer outreach, or charge is created by this project change. No earnings are guaranteed.
