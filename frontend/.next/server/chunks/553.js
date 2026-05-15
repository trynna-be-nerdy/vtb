exports.id=553,exports.ids=[553],exports.modules={2261:(e,t,n)=>{var a={"./v1.10.100/build/pdf.js":4417,"./v1.10.88/build/pdf.js":2350,"./v1.9.426/build/pdf.js":7344,"./v2.0.550/build/pdf.js":5630};function i(e){return n(r(e))}function r(e){if(!n.o(a,e)){var t=Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}return a[e]}i.keys=function(){return Object.keys(a)},i.resolve=r,e.exports=i,i.id=2261},7017:(e,t,n)=>{"use strict";n.d(t,{dj:()=>y,Sh:()=>E,IL:()=>v,CP:()=>g,b$:()=>_,Qx:()=>f,jx:()=>m,k3:()=>d,sm:()=>S,KT:()=>p,Mo:()=>h,Si:()=>$,$:()=>w});var a=n(8937);let i=globalThis.__sql??(0,a.Z)(process.env.DATABASE_URL??"postgresql://vtb:vtbpassword@localhost:5432/vtb",{max:10,idle_timeout:20,connect_timeout:10}),r=new Set(["meeting_date","created_at","updated_at","started_at","finished_at"]);function s(e){return Object.fromEntries(Object.entries(e).map(([e,t])=>t instanceof Date?r.has(e)&&t.toISOString().endsWith("T00:00:00.000Z")?[e,t.toISOString().split("T")[0]]:[e,t.toISOString()]:[e,t]))}function o(e){return e.map(s)}var l=n(3475);let c={"schools-education":"Schools & Education","school-construction":"School Construction","budget-finance":"Budget & Finance",transportation:"Transportation","zoning-land-use":"Zoning & Land Use","public-safety":"Public Safety","policy-governance":"Policy & Governance","equity-inclusion":"Equity & Inclusion",technology:"Technology","community-parks":"Community & Parks",personnel:"Personnel",general:"General"},u=Object.keys(c);async function d(e,t,n){let a=`meetings:list:p=${t}:l=${n}:b=${e}`,r=await (0,l.FE)(a);if(r)return r;let s=(t-1)*n,[c,u]=await Promise.all([e?i`SELECT COUNT(*)::int AS total FROM meetings WHERE processing_status = 'completed' AND board_slug = ${e}`:i`SELECT COUNT(*)::int AS total FROM meetings WHERE processing_status = 'completed'`,e?i`
          SELECT id, title, board_slug, meeting_date, meeting_overview,
                 top_decisions, fiscal_total, total_items, fiscal_items, processing_status
          FROM meetings
          WHERE processing_status = 'completed' AND board_slug = ${e}
          ORDER BY meeting_date DESC
          LIMIT ${n} OFFSET ${s}`:i`
          SELECT id, title, board_slug, meeting_date, meeting_overview,
                 top_decisions, fiscal_total, total_items, fiscal_items, processing_status
          FROM meetings
          WHERE processing_status = 'completed'
          ORDER BY meeting_date DESC
          LIMIT ${n} OFFSET ${s}`]),d=c[0].total,m={meetings:o(u),pagination:{page:t,limit:n,total:d,has_next:t*n<d}};return await (0,l.lK)(a,m),m}async function m(e){let t=`meetings:detail:${e}`,n=await (0,l.FE)(t);if(n)return n;let[a,r,c]=await Promise.all([i`
      SELECT id, title, board_slug, meeting_date, source_url, source_pdf_url,
             meeting_overview, top_decisions, fiscal_total, next_meeting_notes,
             total_items, fiscal_items, processing_status, created_at, updated_at
      FROM meetings WHERE id = ${e}`,i`
      SELECT id, meeting_id, title, summary, decisions, action_items, key_figures,
             primary_category, secondary_tags, urgency, fiscal_impact, affects_schools,
             source_pdf_url, page_range, created_at
      FROM agenda_items WHERE meeting_id = ${e} ORDER BY id`,i`
      SELECT id, meeting_id, title, url, doc_type, created_at
      FROM supporting_documents WHERE meeting_id = ${e}`]);if(0===a.length)return null;let u={meeting:{...s(a[0]),agenda_items:o(r),supporting_documents:o(c)}};return await (0,l.lK)(t,u),u}async function g(){let e="categories:all",t=await (0,l.FE)(e);if(t)return t;let n=await i`
    SELECT primary_category AS slug, COUNT(*)::int AS item_count
    FROM agenda_items
    GROUP BY primary_category`,a=Object.fromEntries(u.map(e=>[e,0]));for(let e of n)e.slug in a&&(a[e.slug]=e.item_count);let r={categories:u.map(e=>({slug:e,label:c[e],item_count:a[e]}))};return await (0,l.lK)(e,r,l.mJ),r}async function _(e,t,n){if(!(e in c))return null;let a=`categories:feed:${e}:p=${t}:l=${n}`,r=await (0,l.FE)(a);if(r)return r;let s=(t-1)*n,[u,d]=await Promise.all([i`SELECT COUNT(*)::int AS total FROM agenda_items WHERE primary_category = ${e}`,i`
      SELECT id, meeting_id, title, summary, primary_category, secondary_tags, urgency,
             fiscal_impact, affects_schools, source_pdf_url, page_range, created_at
      FROM agenda_items
      WHERE primary_category = ${e}
      ORDER BY created_at DESC
      LIMIT ${n} OFFSET ${s}`]),m=u[0].total,g={slug:e,label:c[e],items:o(d),pagination:{page:t,limit:n,total:m,has_next:t*n<m}};return await (0,l.lK)(a,g),g}async function p(e,t,n){let a=`search:${e}:p=${t}:l=${n}`,r=await (0,l.FE)(a);if(r)return r;let s=(t-1)*n,[c,u]=await Promise.all([i`
      SELECT COUNT(*)::int AS total FROM agenda_items
      WHERE search_vector @@ plainto_tsquery('english', ${e})`,i`
      SELECT
        ai.id, ai.meeting_id, ai.title, ai.summary, ai.primary_category,
        ai.secondary_tags, ai.urgency, ai.fiscal_impact, ai.affects_schools,
        ai.source_pdf_url, ai.page_range, ai.created_at,
        m.title AS meeting_title,
        m.meeting_date,
        m.board_slug,
        ts_rank(ai.search_vector, plainto_tsquery('english', ${e})) AS rank
      FROM agenda_items ai
      JOIN meetings m ON ai.meeting_id = m.id
      WHERE ai.search_vector @@ plainto_tsquery('english', ${e})
      ORDER BY rank DESC
      LIMIT ${n} OFFSET ${s}`]),d=c[0].total,m={query:e,results:o(u),pagination:{page:t,limit:n,total:d,has_next:t*n<d}};return await (0,l.lK)(a,m,l.TN),m}async function f(){let e="health:status",t=await (0,l.FE)(e);if(t)return t;let n=new Date,a=new Date(n.getFullYear(),n.getMonth(),1).toISOString(),[r,s,o]=await Promise.all([i`SELECT started_at, finished_at, status FROM pipeline_runs ORDER BY started_at DESC LIMIT 1`,i`SELECT COUNT(*)::int AS cnt FROM agenda_items WHERE created_at >= ${a}`,i`SELECT COUNT(*)::int AS cnt FROM seen_documents WHERE status IN ('pending', 'processing')`]),c=r[0]??null,u={status:"ok",last_pipeline_run:c?c.started_at instanceof Date?c.started_at.toISOString():c.started_at:null,last_pipeline_status:c?.status??null,items_this_month:s[0].cnt,queue_depth:o[0].cnt};return await (0,l.lK)(e,u,l.eF),u}async function y(){return(await i`
    INSERT INTO pipeline_runs (status, documents_found, documents_processed, items_created)
    VALUES ('running', 0, 0, 0)
    RETURNING id`)[0].id}async function h(e,t){await i`
    UPDATE pipeline_runs SET
      status = ${t.status},
      finished_at = NOW(),
      documents_found = COALESCE(${t.documents_found??null}, documents_found),
      documents_processed = COALESCE(${t.documents_processed??null}, documents_processed),
      items_created = COALESCE(${t.items_created??null}, items_created),
      error_message = COALESCE(${t.error_message??null}, error_message)
    WHERE id = ${e}`}async function E(e){return 0===e.length?new Set:new Set((await i`
    SELECT url FROM seen_documents
    WHERE url = ANY(${e}) AND status = 'completed'`).map(e=>e.url))}async function w(e,t,n){await i`
    INSERT INTO seen_documents (url, sha256, status)
    VALUES (${e}, ${t}, ${n})
    ON CONFLICT (url) DO UPDATE SET sha256 = EXCLUDED.sha256, status = EXCLUDED.status,
      updated_at = NOW()`}async function $(e){let t=await i`
    INSERT INTO meetings (title, board_slug, meeting_date, source_url, source_pdf_url,
                          processing_status, total_items, fiscal_items)
    VALUES (${e.title}, ${e.board_slug}, ${e.meeting_date},
            ${e.source_url??null}, ${e.source_pdf_url??null}, 'processing', 0, 0)
    ON CONFLICT DO NOTHING
    RETURNING id`;return t.length>0?t[0].id:(await i`
    SELECT id FROM meetings WHERE board_slug = ${e.board_slug} AND meeting_date = ${e.meeting_date}`)[0].id}async function S(e){return(await i`
    INSERT INTO agenda_items (
      meeting_id, title, summary, decisions, action_items, key_figures,
      primary_category, secondary_tags, urgency, fiscal_impact, affects_schools,
      source_pdf_url, page_range
    ) VALUES (
      ${e.meeting_id}, ${e.title}, ${e.summary},
      ${i.array(e.decisions)}, ${i.array(e.action_items)},
      ${i.json(e.key_figures)},
      ${e.primary_category}, ${i.array(e.secondary_tags)},
      ${e.urgency}, ${e.fiscal_impact}, ${i.array(e.affects_schools)},
      ${e.source_pdf_url??null}, ${e.page_range??null}
    ) RETURNING id`)[0].id}async function v(e,t,n){await i`
    UPDATE meetings SET
      meeting_overview = ${t.meeting_overview},
      top_decisions = ${i.array(t.top_decisions)},
      fiscal_total = ${t.fiscal_total},
      next_meeting_notes = ${t.next_meeting_notes},
      total_items = ${n.total_items},
      fiscal_items = ${n.fiscal_items},
      processing_status = 'completed',
      updated_at = NOW()
    WHERE id = ${e}`}},8338:(e,t,n)=>{"use strict";n.r(t),n.d(t,{runPipeline:()=>G});var a=n(4770),i=n(7017),r=n(3475);let s=process.env.OLLAMA_BASE_URL??"http://localhost:11434",o=process.env.OLLAMA_MODEL??"gemma4:26b",l=`You are a plain-English rewriter for government meeting documents.
Analyze the official government meeting text below and return ONLY a valid JSON object.
No markdown, no backticks, no explanation before or after the JSON.

Required JSON structure (all fields mandatory):
{
  "title": "<topic in plain English, maximum 10 words>",
  "summary": "<2-4 sentences for a general adult audience, no jargon>",
  "decisions": ["<exact decision or vote in plain language>"],
  "action_items": ["<next step or follow-up action>"],
  "key_figures": {
    "amounts": ["<dollar amounts mentioned>"],
    "vote_tallies": ["<vote results like '5-2 approved'>"],
    "dates": ["<specific dates mentioned>"],
    "schools": ["<specific school names mentioned>"]
  }
}

Government meeting text:
{chunk}`,c=`You are a classifier for local government meeting content.
Analyze the meeting summary below and return ONLY a valid JSON object.
No markdown, no backticks, no text before or after the JSON.

The primary_category MUST be exactly one of these 12 slugs:
schools-education | school-construction | budget-finance | transportation |
zoning-land-use | public-safety | policy-governance | equity-inclusion |
technology | community-parks | personnel | general

Required JSON structure (all fields mandatory):
{
  "primary_category": "<one slug from the list above>",
  "secondary_tags": ["<specific sub-topic tag>"],
  "urgency": "<routine OR notable OR significant>",
  "fiscal_impact": <true or false>,
  "affects_schools": ["<school name if mentioned — empty array if none>"]
}

Meeting summary:
{summary}`,u=`You are a summarizer for local government meetings.
Review all agenda item summaries below from one meeting and return ONLY a valid JSON object.
No markdown, no backticks, no text before or after the JSON.

Required JSON structure (all fields mandatory):
{
  "meeting_overview": "<3-5 sentence overview of the entire meeting for a general audience>",
  "top_decisions": ["<1st most significant decision>", "<2nd>", "<3rd>"],
  "fiscal_total": "<total spending approved as a string like '$2.3M', or null if none>",
  "next_meeting_notes": "<scheduled follow-up items or next meeting info, or null if none>"
}

Agenda item summaries:
{summaries}`,d=new Set(["schools-education","school-construction","budget-finance","transportation","zoning-land-use","public-safety","policy-governance","equity-inclusion","technology","community-parks","personnel","general"]),m=new Set(["routine","notable","significant"]);async function g(e){let t=await fetch(`${s}/api/generate`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:o,prompt:e,stream:!1,format:"json"}),signal:AbortSignal.timeout(6e5)});if(!t.ok)throw Error(`Ollama HTTP ${t.status}`);return(await t.json()).response}async function _(e,t){let n;for(let a=0;a<=2;a++){let i=0===a?e:e+"\n\nCRITICAL: Your previous response was not valid JSON or had missing fields. Return ONLY a raw JSON object — no markdown fences, no backticks, no explanatory text, nothing before or after the opening and closing braces.";try{let e=await g(i),n=JSON.parse(e);return t(n)}catch(e){n=e}}throw Error(`LLM failed after 3 attempts: ${n}`)}async function p(e){return _(l.replace("{chunk}",e),e=>({title:String(e.title??"").split(" ").slice(0,10).join(" "),summary:String(e.summary??""),decisions:Array.isArray(e.decisions)?e.decisions:[],action_items:Array.isArray(e.action_items)?e.action_items:[],key_figures:{amounts:Array.isArray(e.key_figures?.amounts)?e.key_figures.amounts:[],vote_tallies:Array.isArray(e.key_figures?.vote_tallies)?e.key_figures.vote_tallies:[],dates:Array.isArray(e.key_figures?.dates)?e.key_figures.dates:[],schools:Array.isArray(e.key_figures?.schools)?e.key_figures.schools:[]}}))}async function f(e){return _(c.replace("{summary}",e),e=>{let t=String(e.primary_category??"general"),n=String(e.urgency??"routine").toLowerCase();return{primary_category:d.has(t)?t:"general",secondary_tags:Array.isArray(e.secondary_tags)?e.secondary_tags:[],urgency:m.has(n)?n:"routine",fiscal_impact:!!e.fiscal_impact,affects_schools:Array.isArray(e.affects_schools)?e.affects_schools:[]}})}async function y(e){let t=e.join("\n\n---\n\n");return _(u.replace("{summaries}",t),e=>({meeting_overview:String(e.meeting_overview??""),top_decisions:(Array.isArray(e.top_decisions)?e.top_decisions:[]).slice(0,3),fiscal_total:e.fiscal_total?String(e.fiscal_total):null,next_meeting_notes:e.next_meeting_notes?String(e.next_meeting_notes):null}))}let h={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",Accept:"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language":"en-US,en;q=0.9"},E={...h,Accept:"application/json, text/plain, */*"},w="https://webapi.legistar.com/v1/loudouncounty",$=[["supervisor","supervisors"],["planning","planning"],["advisory","advisory"]],S=0;async function v(e){let t=4e3-(Date.now()-S);t>0&&await new Promise(e=>setTimeout(e,t));let n=await fetch(e,{headers:E});if(S=Date.now(),!n.ok)throw Error(`Legistar HTTP ${n.status}: ${e}`);return n.json()}async function O(e){try{let t=`${w}/events/${e}/eventitems?$expand=EventItemAttachments`;for(let e of(await v(t)))for(let t of e.EventItemAttachments??[]){let e=t.MatterAttachmentHyperlink??"";if(e.toLowerCase().endsWith(".pdf"))return e}}catch{}return null}async function T(){let e=`${w}/events?$top=50&$orderby=EventDate desc&$filter=EventAgendaStatusName eq 'Final'`,t=await v(e),n=[];for(let e of t)try{let t=e.EventId;if(!t)continue;let a=String(e.EventDate??""),i=function(e){if(!e)return null;let t=e.match(/^(\d{4}-\d{2}-\d{2})/);return t?t[1]:null}(a);if(!i)continue;let r=String(e.EventBodyName??""),s=function(e){let t=e.toLowerCase();for(let[e,n]of $)if(t.includes(e))return n;return"advisory"}(r),o=`${r} – ${i}`,l=e.EventAgendaFile??e.EventMinutesFile??"";if(!l){let e=await O(t);e&&(l=e)}if(!l)continue;l.startsWith("http")||(l=`https://loudoun.legistar.com${l}`);let c=e.EventInSiteURL??`https://loudoun.legistar.com/MeetingDetail.aspx?ID=${t}`;n.push({url:c,pdf_url:l,title:o,meeting_date:i,board_type:s})}catch{}return n}let A="https://go.boarddocs.com/va/lcps/Board.nsf",b=`${A}/getmeetings?open`,N=`${A}/getAgenda?open`,R=/\/va\/lcps\/Board\.nsf\/files\/[^"']+\.pdf/i,C=0;async function L(e,t=!1){let n=4e3-(Date.now()-C);n>0&&await new Promise(e=>setTimeout(e,n));let a=await fetch(e,{headers:t?E:h});if(C=Date.now(),!a.ok)throw Error(`BoardDocs HTTP ${a.status}: ${e}`);return a}async function k(){let e;try{let t=await L(b,!0),n=await t.json();e=Array.isArray(n)?n:n.meetings??[]}catch(e){return console.warn(`[lcps-scraper] BoardDocs meetings fetch failed: ${e}`),[]}let t=[];for(let n of e)try{let e=n.unique??n.id;if(!e)continue;let a=n.date??n.startDate??"",i=function(e){if(!e)return null;let t=String(e).trim(),n=t.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);if(n){let[,e,t,a]=n;return`${a}-${e.padStart(2,"0")}-${t.padStart(2,"0")}`}if(/^\d{4}-\d{2}-\d{2}$/.test(t))return t;let a=parseInt(t,10);return!isNaN(a)&&a>1e10?new Date(a).toISOString().split("T")[0]:null}(a);if(!i)continue;let r=n.name??n.title??`LCPS Meeting ${a}`,s=null;try{let t=await L(`${N}&id=${e}`);s=function(e){let t;let n=R.exec(e);if(n)return`https://go.boarddocs.com${n[0]}`;let a=/href=["']([^"']*\.pdf)["']/gi;for(;null!==(t=a.exec(e));){let e=t[1];if(e.startsWith("http"))return e;return`https://go.boarddocs.com${e}`}return null}(await t.text())}catch{}s||(s=`${A}/Public/${e}?open`),t.push({url:`${A}/Public/${e}?open`,pdf_url:s,title:r,meeting_date:i,board_type:"lcps"})}catch{}return t}var I=n(9801),x=n(5315),D=n(629);async function M(e){let t;let n=function(e){let t=(0,a.createHash)("sha256").update(e).digest("hex").slice(0,16);return(0,x.join)((0,I.tmpdir)(),`${t}.pdf`)}(e);try{return await (0,D.access)(n),(0,D.readFile)(n)}catch{}for(let a=0;a<3;a++)try{let t=await fetch(e,{headers:{...h,Accept:"application/pdf,*/*"},signal:AbortSignal.timeout(6e4),redirect:"follow"});if(!t.ok)throw Error(`HTTP ${t.status}`);let a=t.headers.get("content-type")??"";if(!a.includes("application/pdf")&&!e.toLowerCase().endsWith(".pdf"))throw Error(`Expected application/pdf, got '${a}'`);let i=Buffer.from(await t.arrayBuffer());return await (0,D.writeFile)(n,i),i}catch(e){t=e,a<2&&await new Promise(e=>setTimeout(e,2**a*1e3))}throw Error(`Failed to download ${e} after 3 attempts: ${t}`)}var F=n(3357),P=n.n(F);async function H(e){let t=await P()(e);return{text:function(e,t){if(t<3)return e;let n=e.split("\n"),a=new Map;for(let e of n){let t=e.trim();t&&a.set(t,(a.get(t)??0)+1)}let i=Math.max(2,Math.floor(.6*t)),r=new Set;return(a.forEach((e,t)=>{e>=i&&r.add(t)}),0===r.size)?e:n.filter(e=>!r.has(e.trim())).join("\n")}(t.text,t.numpages),numPages:t.numpages}}let U=[/(?:Item|ITEM)\s*\d+\.?[A-Z]?/i,/(?:Action|ACTION)\s+(?:Item|ITEM)/i,/(?:Consent|CONSENT)\s+(?:Agenda|AGENDA)/i,/(?:PUBLIC|CITIZEN)\s+(?:HEARING|COMMENT)/i];async function j(e){if(0===e.length)return[];let t=e.map(e=>e.pdf_url),n=await (0,i.Sh)(t),a=e.filter(e=>!n.has(e.pdf_url));return console.log(`[deduplicator] ${e.length} total, ${a.length} new, ${e.length-a.length} skipped`),a}let W=new Set(["schools-education","school-construction","budget-finance","transportation","zoning-land-use","public-safety","policy-governance","equity-inclusion","technology","community-parks","personnel","general"]),q=new Set(["routine","notable","significant"]),B=/^\$[\d,]+(\.\d+)?[KMBkmb]?$/,Y=/^\d+[-–]\d+([-–]\d+)?$/,J=/^https?:\/\/.+/;async function G(){let e=await (0,i.dj)();console.log(`[pipeline] Run ${e} started`),await (0,r.rf)({event:"pipeline_started",run_id:e});try{let[t,n]=await Promise.all([T().catch(e=>(console.warn(`[pipeline] Loudoun scraper failed: ${e}`),[])),k().catch(e=>(console.warn(`[pipeline] LCPS scraper failed: ${e}`),[]))]),a=[...t,...n];console.log(`[pipeline] Discovered ${a.length} documents`),await (0,r.rf)({event:"discovered",count:a.length});let s=await j(a);await (0,i.Mo)(e,{status:"running",documents_found:a.length});let o=0;for(let e of s)try{let t=await K(e);o+=t,await (0,r.rf)({event:"document_processed",url:e.url,items:t})}catch(t){console.error(`[pipeline] Failed to process ${e.url}:`,t),await (0,i.$)(e.pdf_url,"","failed")}await (0,i.Mo)(e,{status:"completed",documents_found:a.length,documents_processed:s.length,items_created:o}),console.log(`[pipeline] Run ${e} completed — ${o} agenda items created`),await (0,r.rf)({event:"pipeline_completed",run_id:e,items_created:o})}catch(n){let t=n instanceof Error?n.message:String(n);throw console.error(`[pipeline] Run ${e} failed:`,n),await (0,i.Mo)(e,{status:"failed",error_message:t}),await (0,r.rf)({event:"pipeline_failed",run_id:e,error:t}),n}}async function K(e){console.log(`[pipeline] Processing: ${e.title}`),await (0,i.$)(e.pdf_url,"","processing");let t=await M(e.pdf_url),n=(0,a.createHash)("sha256").update(t).digest("hex"),{text:r}=await H(t);if(!r.trim())throw await (0,i.$)(e.pdf_url,n,"failed"),Error("PDF has no extractable text");let s=function(e){if(!e.trim())return[];let t=function(e){let t=[],n=null,a=[];for(let i of e){let e=function(e){let t=e.trim();for(let e of U)if(e.test(t))return t;return null}(i);if(null!==e){a.length>0&&t.push([n,a]);let r=function(e){let t=[],n=0;for(let a=e.length-1;a>=0&&(n+=e[a].length+1,t.unshift(e[a]),!(n>=200));a--);return t}(a);n=e,a=[...r,i]}else a.push(i)}return a.length>0&&t.push([n,a]),t}(e.split("\n")),n=[];for(let[e,a]of t){let t=a.join("\n");t.length<=2e3?n.push({text:t,detectedHeader:e,charCount:t.length}):n.push(...function(e,t){let n=[],a="",i=!0;for(let r of e.split("\n")){if(a.length+r.length+1>2e3&&a){let e=a.trimEnd();n.push({text:e,detectedHeader:i?t:null,charCount:e.length}),a="",i=!1}a+=(a?"\n":"")+r}if(a.trim()){let e=a.trimEnd();n.push({text:e,detectedHeader:i?t:null,charCount:e.length})}return n}(t,e))}return n}(r),o=await (0,i.Si)({title:e.title,board_slug:e.board_type,meeting_date:e.meeting_date,source_url:e.url,source_pdf_url:e.pdf_url}),l=[],c=0,u=0,d=new Set;for(let t of s){if(!t.text.trim())continue;let n=await p(t.text),a=await f(n.summary),r=function(e,t){let n=[],a=e.title?.trim()??"";0===a.length?n.push("Title is empty"):a.length>100&&n.push(`Title too long: ${a.length} chars (max 100)`);let i=e.summary?.trim().length??0;for(let t of(i<50?n.push(`Summary too short: ${i} chars (min 50)`):i>500&&n.push(`Summary too long: ${i} chars (max 500)`),W.has(e.primary_category)||n.push(`Invalid primary_category: "${e.primary_category}"`),q.has(e.urgency?.toLowerCase())||n.push(`Invalid urgency: "${e.urgency}"`),"routine"!==e.urgency&&(e.decisions?.length??0)===0&&n.push(`Non-routine item (urgency="${e.urgency}") has no decisions`),e.key_figures.amounts??[])){let e=t?.trim();e&&!B.test(e)&&n.push(`Invalid currency amount: "${e}"`)}for(let t of e.key_figures.vote_tallies??[]){let e=t?.trim();e&&!Y.test(e)&&n.push(`Invalid vote tally: "${e}"`)}let r=a.toLowerCase();return r&&t.has(r)?n.push(`Duplicate agenda item title in this meeting: "${a}"`):r&&t.add(r),J.test(e.source_pdf_url??"")||n.push(`Invalid source_pdf_url: "${e.source_pdf_url}"`),{valid:0===n.length,errors:n}}({title:n.title,summary:n.summary,decisions:n.decisions,primary_category:a.primary_category,urgency:a.urgency,key_figures:n.key_figures,source_pdf_url:e.pdf_url},d);if(!r.valid){console.warn(`[pipeline] Skipping invalid item "${n.title}":`,r.errors);continue}await (0,i.sm)({meeting_id:o,title:n.title,summary:n.summary,decisions:n.decisions,action_items:n.action_items,key_figures:{amounts:n.key_figures.amounts,vote_tallies:n.key_figures.vote_tallies,dates:n.key_figures.dates,schools:n.key_figures.schools},primary_category:a.primary_category,secondary_tags:a.secondary_tags,urgency:a.urgency,fiscal_impact:a.fiscal_impact,affects_schools:a.affects_schools,source_pdf_url:e.pdf_url}),l.push(n.summary),a.fiscal_impact&&c++,u++}if(l.length>0){let e=await y(l);await (0,i.IL)(o,e,{total_items:l.length,fiscal_items:c})}return await (0,i.$)(e.pdf_url,n,"completed"),console.log(`[pipeline] Done: ${e.title} — ${u}/${s.length} items written`),u}}};