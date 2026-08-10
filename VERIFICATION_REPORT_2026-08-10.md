# Card Verification Report — 2026-08-10

This report covers the bulk verification of funding cards in `01_equity/` and `02_grants/`.
Every card that could be checked against its live source was checked on 2026-08-10.

## Summary

**Equity cards (01_equity/) — 497 unverified cards processed:**

| Result | Count | Meaning |
|---|---|---|
| Verified | 179 | Site reached, details confirmed or corrected, card marked VERIFIED |
| Needs manual fetch | 220 | Could not be checked automatically — see the two lists below |
| Junk | 86 | Not a real funder — scraper artifacts from listicle pages (left untouched) |
| Mismatch | 12 | The card's website now serves something unrelated (left UNVERIFIED) |

**Grant cards (02_grants/) — 309 unverified cards processed:**

| Result | Count | Meaning |
|---|---|---|
| Verified | 309 | All checked against fundsforcompanies.fundsforngos.org and marked VERIFIED |
| Of which past deadline | 101 | Verified, but the application deadline has already passed |

## Manual-fetch list (for Ray)

### A. Cards with a website that blocked or failed automated checking (65 cards)

These sites exist on the card but returned an error (bot-blocking 403s, DNS failures, 404s, timeouts).
A human opening them in a normal browser can likely verify them in seconds.

- **500 istanbul** — https://500istanbul.vc/ — getaddrinfo ENOTFOUND 500istanbul.vc (DNS failure, retried)
- **applied ventures** — https://www.appliedventures.com/ — HTTP 503 Service Unavailable on both attempts (card notes bot protection)
- **baillie gifford** — https://bailliegifford.com (and www variant) — HTTP 403 Forbidden on both attempts
- **beco capital** — https://beco.capital/ — getaddrinfo ENOTFOUND beco.capital (DNS failure, 2 attempts)
- **biogeneration ventures** — https://biogenerationventures.com — HTTP 403 Forbidden (2 attempts)
- **booz allen ventures** — https://www.boozallen.com/about/ventures.html — HTTP 404 Not Found (2 attempts); page moved, card website is dead
- **bp ventures** — https://www.bp.com/en/global/bp-ventures.html — HTTP 403 Forbidden (2 attempts); bp.com blocks fetcher
- **bpifrance** — https://www.bpifrance.fr — HTTP 403 Forbidden (2 attempts); site blocks fetcher
- **caperion** — https://www.caperion.de/ — getaddrinfo ENOTFOUND www.caperion.de (DNS failure, twice)
- **catalyst fund** — https://www.catalystfund.vc/ — getaddrinfo ENOTFOUND www.catalystfund.vc (DNS failure, twice)
- **ce innovation capital** — https://ceic.com — getaddrinfo ENOTFOUND ceic.com (DNS failure, twice)
- **clearlake capital** — https://clearlake.com (and https://www.clearlake.com/) — HTTP 403 Forbidden (bot block), twice
- **cogito capital** — https://cogitocapital.vc — getaddrinfo ENOTFOUND cogitocapital.vc (DNS failure, twice)
- **costone capital** — http://www.costonecapital.com — DNS getaddrinfo ENOTFOUND (2 attempts)
- **derayah financial** — https://derayah.com/ returned only page title (JS-rendered); https://derayah.com/en/ HTTP 403 Forbidden
- **dila capital** — https://dila.vc — DNS getaddrinfo ENOTFOUND (also www.dila.vc)
- **disruptech** — https://disruptechvm.com/ — DNS getaddrinfo ENOTFOUND (also www variant); card notes pre-existing SSL/bot-protection issues
- **domo invest** — https://www.domoinvest.com.br/ — fetch returned empty page content on both attempts (likely JS-rendered)
- **earlybird digital east** — https://earlybird.com/digitaleast/ — HTTP 404 Not Found (both with and without trailing slash); parent earlybird.com is live
- **eastern bell capital** — http://www.ebellcap.com — DNS getaddrinfo ENOTFOUND (also bare ebellcap.com)
- **esp capital** — https://espcapital.vc/ — getaddrinfo ENOTFOUND espcapital.vc (both attempts, DNS does not resolve)
- **essence vc** — https://essencevc.com — getaddrinfo ENOTFOUND essencevc.com (also tried www.essencevc.com, same DNS failure)
- **ethos private equity** — https://www.ethos.co.za/ — page fetches but is a JS-only shell; only title "Welcome to Ethos | The Rohatyn Group" visible, investor content not verifiable via fetch
- **first in** — https://firstin.vc — HTTP 503 Service Unavailable (also 503 on https://www.firstin.vc/)
- **genesis partners** — http://www.genesispartners.com — HTTP 503 Service Unavailable (both attempts, http and https)
- **greenhouse capital** — https://greenhouse.cap/ — getaddrinfo ENOTFOUND greenhouse.cap (also www.greenhouse.cap ENOTFOUND on retry); domain not resolving
- **h2o capital** — https://h2o.vc/ — getaddrinfo ESERVFAIL h2o.vc on both attempts (card notes pre-existing SSL/bot-protection issues)
- **honeywell ventures** — https://www.honeywell.com/us/en/honeywell-ventures — HTTP 404 Not Found (retry on apex variant also 404); page removed/moved on honeywell.com
- **indus valley capital** — https://www.indusvalley.vc/ — getaddrinfo ENOTFOUND www.indusvalley.vc (twice); card notes pre-existing SSL/bot-protection issues
- **infinity group** — https://www.infinity-cp.com — getaddrinfo ENOTFOUND www.infinity-cp.com (twice)
- **jic venture growth investments** — https://www.jic-vgi.jp — DNS getaddrinfo ENOTFOUND www.jic-vgi.jp (twice, also /english/); domain may have moved
- **kepple africa ventures** — https://www.kepple-africa-ventures.com/ — DNS getaddrinfo ENOTFOUND (twice); domain appears dead
- **kkr next generation technology** — https://kkr.com — HTTP 403 Forbidden (both kkr.com and www.kkr.com); bot-blocked
- **larsson ventures** — https://larsson.vc/ — DNS getaddrinfo ENOTFOUND larsson.vc (twice); domain appears dead
- **london venture partners** — https://lvp.vc — DNS getaddrinfo ESERVFAIL lvp.vc (twice)
- **manutara ventures** — https://www.manutara.vc/ — DNS error (getaddrinfo ENOTFOUND www.manutara.vc), both attempts
- **matrix partners india** — https://matrixpartners.in/ — HTTP 404 on / and /team (firm likely rebranded; needs manual check)
- **nextrans** — https://www.nextrans.vn/ — DNS error (getaddrinfo ENOTFOUND www.nextrans.vn), both attempts
- **northern arc** — https://www.northernarc.com/ — page loads but is JS-rendered with no readable content (title only); /about-us returned 404
- **old mutual alternative investments** — https://www.oldmutual.co.za/alternative-investments/ — HTTP 403 Forbidden (both attempts)
- **oriental fortune capital** — http://www.ofc.com.cn — DNS failure getaddrinfo ENOTFOUND www.ofc.com.cn (both attempts)
- **pif** — https://www.pif.gov.sa/ — HTTP 403 Forbidden (both attempts)
- **raba partnership** — https://raba.vc/ — DNS failure getaddrinfo ENOTFOUND raba.vc (both attempts)
- **raed ventures** — https://www.raedvc.com/ — DNS failure getaddrinfo ENOTFOUND www.raedvc.com (both attempts)
- **redpoint eventures** — https://rpeventures.com.br/ — DNS failure (getaddrinfo ENOTFOUND rpeventures.com.br), 2 attempts
- **rtx ventures** — https://rtx.com — homepage live (real RTX corporate site) but no RTX Ventures content; /who-we-are/ventures and /ventures both 404; ventures arm needs manual confirmation
- **saab ventures** — https://www.saab.com/about/innovation/saab-ventures — HTTP 404 Not Found (page removed/moved)
- **saudi aramco energy ventures** — https://www.saev.com/ — DNS failure (getaddrinfo ENOTFOUND www.saev.com), 2 attempts; likely folded into Aramco Ventures
- **savannah fund** — https://savannah.vc — HTTP 503 Service Unavailable, 2 attempts
- **serafim ventures** — https://serafim.vc/ — DNS failure (getaddrinfo ENOTFOUND serafim.vc), 2 attempts (card notes prior SSL/bot-protection issues)
- **shanghai venture capital co** — http://www.shvc.com.cn — DNS failure (getaddrinfo ENOTFOUND www.shvc.com.cn), 2 attempts
- **sk hynix ventures** — https://www.skhynix.com/ — live SK hynix corporate site but no mention of any ventures/CVC arm; investor status needs manual confirmation
- **snowpoint ventures** — https://www.snowpointventures.com — getaddrinfo ENOTFOUND (DNS failure, twice)
- **startup stadium** — https://www.startupstadium.vc/ — getaddrinfo ENOTFOUND (DNS failure, twice)
- **sunu capital** — https://sunucapital.com/ — HTTP 404 Not Found (twice)
- **tfx capital** — https://tfxcap.com — HTTP 403 Forbidden (twice; bot-blocked)
- **thales ventures** — https://www.thalesgroup.com/ (and /en) — fetch returned empty page content twice (JS-rendered/bot-blocked)
- **two sigma ventures** — https://twosigmaventures.com — HTTP 503 Service Unavailable (twice)
- **unicorn india ventures** — https://www.unicorniv.com/ — DNS error getaddrinfo ENOTFOUND (twice)
- **venturra capital** — https://www.venturra.id/ — DNS error getaddrinfo ENOTFOUND (twice)
- **vinacapital ventures** — https://vinacapital.com/ventures/ — HTTP 403 Forbidden (twice)
- **vivriti capital** — https://www.vivriticapital.com/ — HTTP 403 Forbidden (twice)
- **wamda capital** — https://www.wamda.com/capital — HTTP 404 Not Found (twice); /capital path may no longer exist on wamda.com
- **wellcome trust** — https://wellcome.org/ — HTTP 403 Forbidden (twice; likely bot block)
- **y combinator continuity** — https://www.ycombinator.com/continuity/ — HTTP 404 Not Found (retried without trailing slash, also 404; YC Continuity fund likely discontinued)

### B. Cards with no website at all (155 cards)

These cards have `Website: Unspecified` — there is no URL to open. Someone needs to find the
organization's website before the card can be verified. Card names:

- 10 3one4 capital
- 10 khosla ventures
- 11 chiratae ventures
- 11 greylock
- 12 india quotient
- 12 menlo ventures
- 13 benchmark
- 13 fireside ventures
- 14 new enterprise associates (nea)
- 14 prime venture partners
- 15 first round capital
- 15 stellaris venture partners
- 16 foundry group
- 16 waterbridge ventures
- 17 index ventures
- 17 together fund
- 18 8vc
- 18 iron pillar
- 19 jungle ventures
- 19 lux capital
- 1 andreessen horowitz (a16z)
- 20 dst global (india)
- 20 tiger global management
- 20vc (the twenty minute vc)
- 2 accel
- 2 sequoia capital
- 3 lightspeed venture partners
- 3 z47 (formerly matrix partners india)
- 4 accel
- 4 nexus venture partners
- 5 kalaari capital
- 5 kleiner perkins
- 6 blume ventures
- 6 founders fund
- 7 bessemer venture partners
- 7 elevation capital (formerly saif partners)
- 8 general catalyst
- 8 tiger global (india)
- 9 lightspeed india partners
- 9 spark capital
- acurio ventures
- advantage capital
- afex
- almi invest
- ampli ventures
- antalpha
- aozora corporate investment
- artesian vc
- atlantica ventures
- axon partners group
- bdc venture capital
- beenext
- beenext capital
- big sur ventures
- bonangels venture partners
- bossanova investimentos
- c4 ventures
- caffeinated capital
- callaghan innovation
- canary ventures
- capstone partners
- cardumen capital
- constant ventures
- coventures
- crossboundary
- crowdcube
- delight ventures
- dgf
- domovc
- dsg consumer partners
- eight roads ventures
- enza capital
- eqt
- european innovation council
- f2 venture capital
- fastercapital
- febe ventures
- felicis
- flybridge
- fonds de solidarité ftq
- forge ventures
- forum ventures
- georgian
- global brain corporation
- golden ventures
- goldman sachs
- goodwater capital
- google ventures
- greylock
- grow venture partners
- hashkey capital
- hatcher+
- hetz ventures
- hi ventures
- hsg
- htgf (high tech gruenderfonds)
- hummingbird ventures
- icf capital
- imm investment
- indicator capital
- indiebio (sosv sf and ny)
- innohub mexico venture builder
- international finance corporation
- inveready
- iris
- iterative
- k fund
- kadan capital
- kakao ventures
- kawisafi ventures
- korea development bank
- korea investment partners
- launch
- luminar ventures
- madrona
- magellan technology investment
- matrix
- matrix partners china
- mayfield fund
- mindset ventures
- mitsubishi ufj capital
- mizuho capital
- new enterprise associates
- newchip accelerator
- nissay capital
- norwest
- ntt docomo ventures
- omers ventures
- pale blue dot
- pitango vc
- pontifax
- proeza ventures
- redpoint
- right side capital management
- sbi investment
- sbva
- seaya
- smbc venture capital
- smilegate investment
- sofinnova partners
- sound bioventures
- spectra investments
- spintop ventures
- supernova invest
- technology development fund
- the ark fund
- theventures
- tnb aura
- unpopular ventures
- uob venture
- us venture partners
- version one ventures
- whitecap venture partners
- wow aceleradora
- zedcrest capital limited

## Junk cards (86 cards)

These equity cards are not funders at all — they are fragments accidentally scraped from
"top VC" listicle pages (section headings, FAQ questions, navigation links, table headers).
They were **left untouched**: whether to delete them is a decision for Ray.

- **20 top venture capital firms in india (2026)** — Card is the listicle article title itself ("20 Top Venture Capital Firms in India (2026)"), not a funding organization
- **60% off** — Scraper artifact — promo banner text "60% off" from basetemplates.com listicle, not an organization
- **americas** — Wikipedia list-page section heading scraped as an org, no website
- **asia** — Wikipedia list-page section heading scraped as an org, no website
- **assets under management** — Wikipedia table column header scraped as an org, no website
- **best 5 australia vcs at a glance** — Listicle section heading scraped from waveup.com blog, not an organization
- **best 5 germany vcs at a glance** — Listicle section heading scraped from waveup.com blog, not an organization
- **broader lists** — Page section fragment ("Broader lists") scraped from shizune.co listicle, not an organization
- **by city** — OpenVC site navigation fragment ("By city"), not an organization
- **by country** — OpenVC site navigation fragment ("By country"), not an organization
- **by industry** — OpenVC site navigation fragment ("By industry"), not an organization
- **by investor type** — OpenVC site navigation fragment ("By investor type"), not an organization
- **by stage** — OpenVC site navigation fragment ("By stage"), not an organization
- **can i raise pre seed or seed funding on openvc** — Scraped FAQ heading from OpenVC page, not an organization
- **capital raised** — Wikipedia table column header scraped as an org name
- **check it out ** — Scraped call-to-action button text from basetemplates listicle, not an organization
- **claim your investor profile on openvc** — Scraped promo banner from OpenVC page, not an organization
- **colaborativo** — Lowercase generic Spanish word scraped from failory Mexico listicle; no website, no contact — page fragment
- **contents** — Wikipedia "Contents" table-of-contents fragment scraped as an org name
- **deal flow** — "Deal flow" is a generic finance term scraped from Wikipedia's List-of-VC-firms page, not an organization
- **emea** — Not an organization — region-heading fragment scraped from Wikipedia "List of venture capital firms"; no website
- **frequently asked questions** — Scraper artifact — "Frequently Asked Questions" section heading from quintedge.com India VC listicle, not an organization
- **geography** — Listicle page fragment ("Geography" heading from latitud.com), not an organization
- **germany sub niches which one matches your raise** — Blog article section heading from waveup.com listicle, not an organization
- **get fin free for 1 year with openvc** — OpenVC promo banner scraped as a card, not an organization
- **get intercom free for 1 year with openvc** — OpenVC promo banner scraped as a card, not an organization
- **go from zero to one** — Marketing tagline fragment from latitud.com, not an organization
- **hottest industries for vcs in the united states** — OpenVC article/FAQ heading scraped as a card, not an organization
- **how can i find investors for my startup** — OpenVC FAQ question scraped as a card, not an organization
- **how do i pitch investors on openvc** — OpenVC FAQ question scraped as a card, not an organization
- **how do vc firms in india hire** — Quintedge blog FAQ heading scraped as a card, not an organization
- **how do you break into venture capital in india** — listicle FAQ heading scraped as an org, no website
- **how to break into venture capital in india** — duplicate listicle FAQ heading scraped as an org, no website
- **how to raise venture capital in australia in 2026** — article title scraped as an org, no website
- **how to raise venture capital in germany in 2026** — article title scraped as an org, no website
- **how vc firms in india hire** — article section heading scraped as an org, no website
- **investors by country** — shizune.co site-navigation fragment scraped as an org, no website
- **investors by industry** — shizune.co site-navigation fragment scraped as an org, no website
- **is openvc free to use** — FAQ question scraped as an org, no website
- **list** — Scraper artifact: "List" from Wikipedia "List of venture capital firms" page title, not an organization
- **methodology — how we keep this list current** — Scraped section heading from waveup listicle, not an organization
- **more investor lists** — Scraped navigation/section heading from openvc.app, not an organization
- **most active australia venture capital funds** — Scraped section heading from waveup listicle, not an organization
- **most active germany venture capital funds** — Scraped section heading from waveup listicle, not an organization
- **openvc startups have raised$1+ billion from** — Scraper fragment — page heading "OpenVC startups have raised $1+ billion from:" is not an organization
- **overview** — Scraper fragment — "Overview" is a page section heading from a basepoint.vc listicle, not an organization
- **portfolio companies** — Scraper fragment — "Portfolio companies" is a page section heading from latitud.com, not an organization
- **quick facts about us startup investment** — Scraper fragment — "Quick Facts About U.S. Startup Investment" is an article section heading from openvc.app, not an organization
- **ready to build your vc career** — Scraper fragment — "Ready to Build Your VC Career?" is a promo CTA from a quintedge.com blog article, not an organization
- **references** — Wikipedia page section heading ("References") scraped as an org
- **refine your thesis** — latitud.com page fragment / CTA text, not an organization
- **related** — listicle page fragment ("Related"), not an organization
- **related posts** — blog widget heading ("Related Posts"), not an organization
- **saas vc funds in africa** — shizune.co listicle title scraped as an org, not a funder
- **sectors** — latitud.com nav/section heading ("Sectors"), not an organization
- **see also** — Wikipedia page section heading ("See also") scraped as an org
- **seo outsourcing guide for startups** — waveup.com blog article title, not an organization
- **start building your shortlist** — scraper fragment — OpenVC page call-to-action text, not an organization
- **technologies** — scraper fragment — truncated page text from latitud.com, not an organization name
- **the 20 best venture capital firms in the us** — scraper fragment — OpenVC listicle headline, not an organization
- **theres no too early** — scraper fragment — Latitud marketing slogan, not an organization
- **top vc cities in the us** — listicle section heading from openvc.app scrape, not an organization
- **top vc funded us startups (2023–2024)** — listicle section heading from openvc.app scrape, not an organization
- **trusted by latams top founders and investors** — marketing banner fragment from latitud.com scrape, not an organization
- **useful resources for american startup founders** — page section heading from openvc.app scrape, not an organization
- **vc funds** — generic listicle heading from basepoint.vc scrape, not an organization
- **vc salary benchmarks in india (2026)** — salary/benchmark article heading from quintedge blog scrape, not an organization
- **venture capital studio** — generic page fragment from failory listicle scrape, no website, not an identifiable organization
- **we come in early** — tagline fragment from latitud.com scrape, not an organization
- **what are vc salary benchmarks in india (2026)** — FAQ heading from quintedge blog scrape, not an organization
- **what founders are saying** — testimonial section fragment from latitud.com scrape, not an organization
- **what is a venture capital firm** — FAQ heading from openvc.app scrape, not an organization
- **what is openvc ** — FAQ heading from openvc.app scrape, not an organization
- **what startups have raised capital with openvc** — FAQ heading from openvc.app scrape, not an organization
- **what you get** — Latitud page fragment ("What you get" section heading), not an organization
- **where are most of the top vc firms located** — OpenVC FAQ heading scraped as an org
- **where the money is going in 2025–2026** — Waveup blog section heading scraped as an org
- **who are tier 1 vcs** — OpenVC FAQ heading scraped as an org
- **who is behind openvc** — OpenVC FAQ heading scraped as an org
- **who is openvc for** — OpenVC FAQ heading scraped as an org
- **why australia founders need australia vcs** — Waveup blog section heading scraped as an org
- **why do founders raise with openvc** — OpenVC FAQ heading scraped as an org
- **why germany founders need germany vcs** — Waveup blog section heading scraped as an org
- **why india’s vc landscape is booming in 2026** — Quintedge blog section heading scraped as an org
- **why is india’s vc landscape booming in 2026** — Quintedge blog section heading scraped as an org (duplicate of above)
- **youre here if** — Latitud page fragment ("You're here if" section heading), not an organization

## Mismatches (12 cards)

These cards have a website that loads, but it no longer belongs to the funder — the domain is
parked, for sale, or serving an unrelated business. All were left UNVERIFIED.

- **1789 capital** — https://1789.vc is a domain-for-sale listing on Spaceship.com, not 1789 Capital's site; card left UNVERIFIED
- **advanced technology ventures** — atv.com is an all-terrain-vehicle review site (VerticalScope Inc.), not the VC firm — left UNVERIFIED
- **all iron ventures** — alliron.vc 301-redirects to vdcx.io, a Vietnamese online gambling portal (GO88); no All Iron content
- **arzan venture capital** — arzanvc.com 301-redirects to noboring.tech, a bare "Coming Soon" placeholder (contact info@arzanvc.com) with no investor content
- **base partners** — basepartners.com is a bare landing page (data-center photo + info@ email), no VC/investor content; likely not the Brazilian VC (which uses a different domain)
- **cohort capital** — cohortcapital.com is a live site but for a London property bridging-loan lender (unregulated short-term real estate finance), not a tech seed VC
- **ignitetech** — live site (now ignitetech.ai) but it is an AI-first enterprise software company in Austin TX, not an investor/VC — card's "Corporate VC" claim unsupported
- **intudo ventures** — intudo.vc 302s to domains.atom.com domain-sale page — parked/for-sale domain, no live Intudo Ventures site
- **maersk growth** — maersk.com is live but is the Maersk logistics/shipping site; no mention of Maersk Growth venture arm anywhere; source URL is a ground-freight promo banner link — left UNVERIFIED
- **ohio techangel funds** — rev1ventures.com is live but is Rev1 Ventures (Columbus OH venture studio); site makes no mention of Ohio TechAngel Funds — left UNVERIFIED
- **razors edge ventures** — www.razorsedge.com is live but is a creative/storytelling portfolio ("Razor's Edge Communications"), not the VC firm — left UNVERIFIED
- **red dot capital partners** — reddotcap.com is a generic GoDaddy landing page ("Your Satisfaction, Our Mission", contact form only); /team/ returns 404 — not the Israeli VC's site

## Expired grants (101 cards)

These grants were verified as accurate, but their application deadline is already past
(all deadlines before 2026-08-10). They may be worth archiving or watching for the next cycle.

- 2026-05-14 Applications open for MG Developer Program and Grant India
- 2026-05-14 Open Call Advanced Connectivity Technologies United Kingdom
- 2026-05-15 Call for Advanced Computing Project for Scientific and Technological Innovation Portug
- 2026-05-15 Open Call Work to Zero Fatigue Pilot Grant 2026 US
- 2026-05-16 CFAs Youth Participation at the 36th Malawi International Trade Fair
- 2026-05-17 Apply for Climate Tech Catalyst Acceleration Program Vietnam
- 2026-05-17 Bold Spirit Award Grants for Small Business Owners Canada
- 2026-05-17 Open Call Next Generation Mobility Project 2026 Thailand
- 2026-05-18 CFPs Development of a Citizen Engagement and Digital Platform Lesotho
- 2026-05-18 Mini-Grant Competition for Summer Playground Arrangement Ukraine
- 2026-05-20 Apply for Cummins and Venture Center CSR Funding Program India
- 2026-05-20 CFAs Regional Climate Risk Monitoring for Pacific Islands Fiji
- 2026-05-20 Call for Production of Parent-Child Communication TV Drama Series on SRHR
- 2026-05-22 Call for Participation in Waste Management and Recycling Support Program Moldova
- 2026-05-22 Funding Available for Women-Led Agribusinesses in Nigeria
- 2026-05-22 Just Transition Fund for the North East and Moray United Kingdom
- 2026-05-22 Open Call Zepto Nova Pitch in 10 Programme India
- 2026-05-22 RFAs Good Governance Framework Development and Public Sector Reform Initiative Malaysi
- 2026-05-24 AfCFTA Startup Acceleration and Partnership Program
- 2026-05-24 Call for Applications Young Professionals Bootcamp Nigeria
- 2026-05-24 Contract Opportunity for IT Software Firm to Develop Digital Legal Aid System 8211 Ban
- 2026-05-24 Entries Open Greenovation Renewable Energy for Livelihood Challenge India
- 2026-05-24 Nominations open for Greenovation Urban Climate Resilience Challenge India
- 2026-05-25 Open Call Mangrove Conservation Grant Programme in Suriname
- 2026-05-25 RFPs Hands-On ToT Programme for MSME Competitiveness and Export Initiative Afghanistan
- 2026-05-27 Apply Now iHatch Cohort 5 Startups Incubation Programme Nigeria
- 2026-05-27 CFAs Aid for the International Distribution of Spanish Films Spain
- 2026-05-29 Accelerator 2026 Programme for Digital Tech Startups
- 2026-05-29 Adopt a Park Initiative under Urban Revitalisation Programme South Africa
- 2026-05-29 Open Call for Kick-Start Proposals Supporting Space Technology Services
- 2026-05-31 Asian Institute of Management  Dado Banatao Incubator Program Philippines
- 2026-05-31 Call for Proposals Investment Ready Program Australia
- 2026-05-31 Call for Research Study on Legislative Gaps in Violence Prevention Palestine
- 2026-05-31 Fifth Call for Funding Applications FUNGUO Innovation Programme Tanzania
- 2026-05-31 International Spacetech Startup Supporting Program
- 2026-05-31 RFAs GICAT Innovation Competition at EUROSATORY 2026 France
- 2026-05-31 Request for Applications Entrepreneurship World Cup 2026
- 2026-06-01 Applications open for World Startup Championship 2026 Pakistan
- 2026-06-01 Call for Proposals Bringing Living Heritage into Classroom Philippines
- 2026-06-01 RFPs Workplace Gender-Based Violence Study
- 2026-06-03 Call for Applications Private Sector Pathways Program Australia
- 2026-06-04 Applications open for Orange Corners Innovation Fund Benin
- 2026-06-05 CFAs COEPs BHAU Institute Launches Social Innovation Summit India
- 2026-06-05 Nominations open for Hydrogen TCP Awards of Excellence
- 2026-06-10 Call for Proposals UPES DST-iTBI Ignition Grant India
- 2026-06-11 Applications open for Social Projects Castilla-La Mancha 2026 Spain
- 2026-06-11 Call for Social Projects Castile and León 2026 Spain
- 2026-06-14 Apply Now GITA Innovative Startup Acceleration Program 2026 Georgia
- 2026-06-14 Call for Applications Water and Sanitation Enterprises in Ethiopia
- 2026-06-15 Apply Now TribePreneurs Idea Quest for Tribal Startups India
- 2026-06-15 CFAs Tribal Business Conclave Open Grand Challenge India
- 2026-06-15 Call for Startups Accelerate the Future of Sustainable Food
- 2026-06-15 Request for Applications Cascador ScaleUp Programme
- 2026-06-17 Entries open for K-Startup Grand Challenge Programme
- 2026-06-17 PHC Bosphore is the Franco-Turkish Hubert Curien Partnership France
- 2026-06-17 Request for Applications Defra Farming Innovation Investor Partnership UK
- 2026-06-18 Big Dreams Grant for Small Business Growth in United States
- 2026-06-19 Applications Open for L-CAMP Vietnam Program 2026
- 2026-06-21 Call for Proposals Water and Sanitation Enterprises Cambodia
- 2026-06-24 Applications open for Farm Solar Grants Canada
- 2026-06-26 Funding for Hungarian Organisations in Horizon Europe Partnership Projects
- 2026-06-28 Construction Startup Competition 2026 10th Edition
- 2026-06-30 Apply Now Naaripreneur for Her Program Cohort 8211 2 India
- 2026-06-30 CFAs Google for Startups Accelerator Programme
- 2026-06-30 Funding for Domestic and International Intellectual Property Protection Activities Hun
- 2026-07-03 Meaningful Business 100 MB100 Award Programme 2026
- 2026-07-10 Nominations open for Hume Business Awards in Australia
- 2026-07-15 Open Call Marketing Grant  Micro Stream Canada
- 2026-07-15 RFAs Support for Hungarian Participation in the EUREKA Programme
- 2026-07-17 Call for Bilateral Science and Innovation Projects Turkey and Slovak Republic
- 2026-07-19 Applications open for JKEDI Startup Seed Funding Programme  India 
- 2026-07-20 Global Startup EXPO 2026 Call for Deep-Tech Startups Japan
- 2026-07-20 RFAs Promoting Ukrainian Startups and Innovation Ecosystem
- 2026-07-21 Call for Thailand Joint Industrial Technology Pilot Projects
- 2026-07-21 Taiwan-Israel Research and Development Pilot Cooperation Program
- 2026-07-23 Call for Applications Adapted Crops for Resilience and Green Jobs
- 2026-07-24 Apply now for Skills Hubs of Excellence Initiative
- 2026-07-24 Call for Applications CDL Program8217s Oceans Stream
- 2026-07-24 Call for Applications  Startup Acceleration Programme  India 
- 2026-07-24 ICAR SHITIJ 20 Startup Incubation Program for Agriculture Innovation India
- 2026-07-25 INFO Grants to Support Innovative Companies with Technological Potential and Scalabili
- 2026-07-26 Google DeepMind Accelerator Program 8211 AI for the Planet
- 2026-07-27 Funding Opportunity to Promote Healthy and Respectful Relationships in Schools UK
- 2026-07-29 CFPs Pilot Line Programme for Semiconductor Innovation Sweden
- 2026-07-31 Applications Open Kluz Prize for PeaceTech 2026
- 2026-07-31 Applications open for Circular Solutions for Communities Serbia
- 2026-07-31 CFAs Innovations in Decentralized Pan-Orthoebolavirus Diagnostics
- 2026-07-31 CFPs Leveraging IFADs Rural Sector Performance Assessment for Policy and Investment
- 2026-07-31 Call for Applications New Solutions Social Innovation Lab Program Ireland
- 2026-07-31 Call for Proposals Pcieerd Startup Grant Fund Program Philippines
- 2026-07-31 RFAs Public Affairs Support for Better Air Quality Regulation
- 2026-07-31 US-India Technology Innovation Partnership Grant
- 2026-08-03 CFPs Arts Culture and Sports Peace Initiative Grant Malaysia
- 2026-08-03 Cynnal y Cardi 8211 Local Growth Fund 2026-2027 UK
- 2026-08-03 LASR Bilateral Cooperation Call for Joint R038D Projects Turkey and Libya
- 2026-08-05 Grants for Reducing Veteran Homelessness Programme United Kingdom
- 2026-08-06 Environmental Grants for Sustainable Initiatives Namibia
- 2026-08-09 Apply Now AI NATION Accelerator for AI Startups Germany
- 2026-08-09 Open Call AI NATION GRANT for Early-Stage AI Founder Teams Germany
- 2026-08-09 Open Call Human Libraries Project Grant Opportunity United Kingdom
- 2026-08-15 CFAs Sanabil Accelerator Programme for High-Growth Tech Startups

