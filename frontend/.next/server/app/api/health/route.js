"use strict";(()=>{var e={};e.id=829,e.ids=[829],e.modules={399:e=>{e.exports=require("next/dist/compiled/next-server/app-page.runtime.prod.js")},517:e=>{e.exports=require("next/dist/compiled/next-server/app-route.runtime.prod.js")},7790:e=>{e.exports=require("assert")},8893:e=>{e.exports=require("buffer")},4770:e=>{e.exports=require("crypto")},665:e=>{e.exports=require("dns")},7702:e=>{e.exports=require("events")},2048:e=>{e.exports=require("fs")},8216:e=>{e.exports=require("net")},9801:e=>{e.exports=require("os")},5315:e=>{e.exports=require("path")},6119:e=>{e.exports=require("perf_hooks")},6162:e=>{e.exports=require("stream")},4026:e=>{e.exports=require("string_decoder")},2452:e=>{e.exports=require("tls")},4175:e=>{e.exports=require("tty")},7360:e=>{e.exports=require("url")},1764:e=>{e.exports=require("util")},519:(e,t,a)=>{a.r(t),a.d(t,{originalPathname:()=>E,patchFetch:()=>f,requestAsyncStorage:()=>m,routeModule:()=>d,serverHooks:()=>g,staticGenerationAsyncStorage:()=>p});var s={};a.r(s),a.d(s,{GET:()=>_,dynamic:()=>c,runtime:()=>u});var i=a(9303),r=a(8716),n=a(670),o=a(7070),l=a(7017);let u="nodejs",c="force-dynamic";async function _(){try{let e=await (0,l.Qx)();return o.NextResponse.json(e)}catch(e){return console.error("/api/health error:",e),o.NextResponse.json({status:"error",error:"Internal server error"},{status:500})}}let d=new i.AppRouteRouteModule({definition:{kind:r.x.APP_ROUTE,page:"/api/health/route",pathname:"/api/health",filename:"route",bundlePath:"app/api/health/route"},resolvedPagePath:"C:\\Users\\sriva\\vtb\\frontend\\app\\api\\health\\route.ts",nextConfigOutput:"",userland:s}),{requestAsyncStorage:m,staticGenerationAsyncStorage:p,serverHooks:g}=d,E="/api/health/route";function f(){return(0,n.patchFetch)({serverHooks:g,staticGenerationAsyncStorage:p})}},7017:(e,t,a)=>{a.d(t,{dj:()=>f,Sh:()=>S,IL:()=>R,CP:()=>m,b$:()=>p,Qx:()=>E,jx:()=>d,k3:()=>_,sm:()=>h,KT:()=>g,Mo:()=>y,Si:()=>T,$:()=>O});var s=a(8937);let i=globalThis.__sql??(0,s.Z)(process.env.DATABASE_URL??"postgresql://vtb:vtbpassword@localhost:5432/vtb",{max:10,idle_timeout:20,connect_timeout:10}),r=new Set(["meeting_date","created_at","updated_at","started_at","finished_at"]);function n(e){return Object.fromEntries(Object.entries(e).map(([e,t])=>t instanceof Date?r.has(e)&&t.toISOString().endsWith("T00:00:00.000Z")?[e,t.toISOString().split("T")[0]]:[e,t.toISOString()]:[e,t]))}function o(e){return e.map(n)}var l=a(3475);let u={"schools-education":"Schools & Education","school-construction":"School Construction","budget-finance":"Budget & Finance",transportation:"Transportation","zoning-land-use":"Zoning & Land Use","public-safety":"Public Safety","policy-governance":"Policy & Governance","equity-inclusion":"Equity & Inclusion",technology:"Technology","community-parks":"Community & Parks",personnel:"Personnel",general:"General"},c=Object.keys(u);async function _(e,t,a){let s=`meetings:list:p=${t}:l=${a}:b=${e}`,r=await (0,l.FE)(s);if(r)return r;let n=(t-1)*a,[u,c]=await Promise.all([e?i`SELECT COUNT(*)::int AS total FROM meetings WHERE processing_status = 'completed' AND board_slug = ${e}`:i`SELECT COUNT(*)::int AS total FROM meetings WHERE processing_status = 'completed'`,e?i`
          SELECT id, title, board_slug, meeting_date, meeting_overview,
                 top_decisions, fiscal_total, total_items, fiscal_items, processing_status
          FROM meetings
          WHERE processing_status = 'completed' AND board_slug = ${e}
          ORDER BY meeting_date DESC
          LIMIT ${a} OFFSET ${n}`:i`
          SELECT id, title, board_slug, meeting_date, meeting_overview,
                 top_decisions, fiscal_total, total_items, fiscal_items, processing_status
          FROM meetings
          WHERE processing_status = 'completed'
          ORDER BY meeting_date DESC
          LIMIT ${a} OFFSET ${n}`]),_=u[0].total,d={meetings:o(c),pagination:{page:t,limit:a,total:_,has_next:t*a<_}};return await (0,l.lK)(s,d),d}async function d(e){let t=`meetings:detail:${e}`,a=await (0,l.FE)(t);if(a)return a;let[s,r,u]=await Promise.all([i`
      SELECT id, title, board_slug, meeting_date, source_url, source_pdf_url,
             meeting_overview, top_decisions, fiscal_total, next_meeting_notes,
             total_items, fiscal_items, processing_status, created_at, updated_at
      FROM meetings WHERE id = ${e}`,i`
      SELECT id, meeting_id, title, summary, decisions, action_items, key_figures,
             primary_category, secondary_tags, urgency, fiscal_impact, affects_schools,
             source_pdf_url, page_range, created_at
      FROM agenda_items WHERE meeting_id = ${e} ORDER BY id`,i`
      SELECT id, meeting_id, title, url, doc_type, created_at
      FROM supporting_documents WHERE meeting_id = ${e}`]);if(0===s.length)return null;let c={meeting:{...n(s[0]),agenda_items:o(r),supporting_documents:o(u)}};return await (0,l.lK)(t,c),c}async function m(){let e="categories:all",t=await (0,l.FE)(e);if(t)return t;let a=await i`
    SELECT primary_category AS slug, COUNT(*)::int AS item_count
    FROM agenda_items
    GROUP BY primary_category`,s=Object.fromEntries(c.map(e=>[e,0]));for(let e of a)e.slug in s&&(s[e.slug]=e.item_count);let r={categories:c.map(e=>({slug:e,label:u[e],item_count:s[e]}))};return await (0,l.lK)(e,r,l.mJ),r}async function p(e,t,a){if(!(e in u))return null;let s=`categories:feed:${e}:p=${t}:l=${a}`,r=await (0,l.FE)(s);if(r)return r;let n=(t-1)*a,[c,_]=await Promise.all([i`SELECT COUNT(*)::int AS total FROM agenda_items WHERE primary_category = ${e}`,i`
      SELECT id, meeting_id, title, summary, primary_category, secondary_tags, urgency,
             fiscal_impact, affects_schools, source_pdf_url, page_range, created_at
      FROM agenda_items
      WHERE primary_category = ${e}
      ORDER BY created_at DESC
      LIMIT ${a} OFFSET ${n}`]),d=c[0].total,m={slug:e,label:u[e],items:o(_),pagination:{page:t,limit:a,total:d,has_next:t*a<d}};return await (0,l.lK)(s,m),m}async function g(e,t,a){let s=`search:${e}:p=${t}:l=${a}`,r=await (0,l.FE)(s);if(r)return r;let n=(t-1)*a,[u,c]=await Promise.all([i`
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
      LIMIT ${a} OFFSET ${n}`]),_=u[0].total,d={query:e,results:o(c),pagination:{page:t,limit:a,total:_,has_next:t*a<_}};return await (0,l.lK)(s,d,l.TN),d}async function E(){let e="health:status",t=await (0,l.FE)(e);if(t)return t;let a=new Date,s=new Date(a.getFullYear(),a.getMonth(),1).toISOString(),[r,n,o]=await Promise.all([i`SELECT started_at, finished_at, status FROM pipeline_runs ORDER BY started_at DESC LIMIT 1`,i`SELECT COUNT(*)::int AS cnt FROM agenda_items WHERE created_at >= ${s}`,i`SELECT COUNT(*)::int AS cnt FROM seen_documents WHERE status IN ('pending', 'processing')`]),u=r[0]??null,c={status:"ok",last_pipeline_run:u?u.started_at instanceof Date?u.started_at.toISOString():u.started_at:null,last_pipeline_status:u?.status??null,items_this_month:n[0].cnt,queue_depth:o[0].cnt};return await (0,l.lK)(e,c,l.eF),c}async function f(){return(await i`
    INSERT INTO pipeline_runs (status, documents_found, documents_processed, items_created)
    VALUES ('running', 0, 0, 0)
    RETURNING id`)[0].id}async function y(e,t){await i`
    UPDATE pipeline_runs SET
      status = ${t.status},
      finished_at = NOW(),
      documents_found = COALESCE(${t.documents_found??null}, documents_found),
      documents_processed = COALESCE(${t.documents_processed??null}, documents_processed),
      items_created = COALESCE(${t.items_created??null}, items_created),
      error_message = COALESCE(${t.error_message??null}, error_message)
    WHERE id = ${e}`}async function S(e){return 0===e.length?new Set:new Set((await i`
    SELECT url FROM seen_documents
    WHERE url = ANY(${e}) AND status = 'completed'`).map(e=>e.url))}async function O(e,t,a){await i`
    INSERT INTO seen_documents (url, sha256, status)
    VALUES (${e}, ${t}, ${a})
    ON CONFLICT (url) DO UPDATE SET sha256 = EXCLUDED.sha256, status = EXCLUDED.status,
      updated_at = NOW()`}async function T(e){let t=await i`
    INSERT INTO meetings (title, board_slug, meeting_date, source_url, source_pdf_url,
                          processing_status, total_items, fiscal_items)
    VALUES (${e.title}, ${e.board_slug}, ${e.meeting_date},
            ${e.source_url??null}, ${e.source_pdf_url??null}, 'processing', 0, 0)
    ON CONFLICT DO NOTHING
    RETURNING id`;return t.length>0?t[0].id:(await i`
    SELECT id FROM meetings WHERE board_slug = ${e.board_slug} AND meeting_date = ${e.meeting_date}`)[0].id}async function h(e){return(await i`
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
    ) RETURNING id`)[0].id}async function R(e,t,a){await i`
    UPDATE meetings SET
      meeting_overview = ${t.meeting_overview},
      top_decisions = ${i.array(t.top_decisions)},
      fiscal_total = ${t.fiscal_total},
      next_meeting_notes = ${t.next_meeting_notes},
      total_items = ${a.total_items},
      fiscal_items = ${a.fiscal_items},
      processing_status = 'completed',
      updated_at = NOW()
    WHERE id = ${e}`}},3475:(e,t,a)=>{a.d(t,{AO:()=>n,FE:()=>c,TN:()=>l,eF:()=>u,lK:()=>_,mJ:()=>o,rf:()=>d});var s=a(2197),i=a.n(s);let r=globalThis.__redis??new(i())(process.env.REDIS_URL??"redis://localhost:6379/0",{maxRetriesPerRequest:3,enableReadyCheck:!1,lazyConnect:!0}),n="vtb:updates",o=parseInt(process.env.CACHE_TTL_SECONDS??"900",10),l=parseInt(process.env.SEARCH_CACHE_TTL_SECONDS??"300",10),u=parseInt(process.env.HEALTH_CACHE_TTL_SECONDS??"30",10);async function c(e){try{let t=await r.get(e);return t?JSON.parse(t):null}catch{return null}}async function _(e,t,a=o){try{await r.set(e,JSON.stringify(t),"EX",a)}catch{}}async function d(e){try{await r.publish(n,JSON.stringify(e))}catch{}}}};var t=require("../../../webpack-runtime.js");t.C(e);var a=e=>t(t.s=e),s=t.X(0,[948,898,937,972],()=>a(519));module.exports=s})();