# -*- coding: utf-8 -*-
import subprocess, re, html, csv, os, glob, datetime, urllib.parse

REPO = "/Users/mango/Documents/claude/SWAI_paper"
TODAY = datetime.date.today().isoformat()

def get(url):
    return subprocess.run(["curl","-sL","--compressed","-A","Mozilla/5.0",url],
                          capture_output=True, text=True).stdout

def post(url, data):
    args=["curl","-sL","--compressed","-A","Mozilla/5.0","-X","POST",url]
    for k,v in data.items():
        args += ["--data-urlencode", f"{k}={v}"]
    return subprocess.run(args, capture_output=True, text=True).stdout

def cl(x):
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',x))).strip()

# ---- 관심 키워드 (제목 기반 1차 필터) ----
KW_LATIN = ["AI","SW","STEM","ICT","VR","AR","XR","IoT"]           # 대소문자 구분
KW_KO = ["인공지능","생성형","소프트웨어","자동채점","자동 채점","자동평가","코딩","프로그래밍",
         "컴퓨팅","컴퓨터·정보","컴퓨터.정보","디지털","에듀테크","메타버스","지능정보","챗봇",
         "디지털교과서","미디어 리터러시","미디어 문해","학습분석","데이터","스마트","온라인","원격",
         "이러닝","가상현실","증강현실","공간컴퓨팅","오픈소스","알고리즘","머신러닝","딥러닝",
         "빅데이터","클라우드","사물인터넷","정보교육","정보교과","정보보호","정보윤리","정보과",
         "정보 소양","정보소양","디지털 리터러시","디지털 소양","디지털 전환","디지털 미디어"]
def match_kw(title):
    hits=[]
    for k in KW_LATIN:
        if re.search(r'(?<![A-Za-z])'+re.escape(k)+r'(?![A-Za-z])', title): hits.append(k)
    for k in KW_KO:
        if k in title: hits.append(k)
    # 중복 상위어 정리
    return sorted(set(hits))

# ---- 기존 요약본 식별자 ----
def done_ids(instdir, pat):
    ids=set()
    for f in glob.glob(os.path.join(REPO,"src/reports",instdir,"*.md")):
        s=open(f,encoding="utf-8").read()
        for m in re.finditer(pat, s):
            ids.add(m.group(1))
    return ids

def norm_url(u):
    # utm_* 추적 파라미터 제거 (edpolicy-intl 은 외부 원문 URL 이 곧 고유 키)
    p=urllib.parse.urlsplit(u.strip())
    q=[(k,v) for k,v in urllib.parse.parse_qsl(p.query) if not k.lower().startswith("utm_")]
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,urllib.parse.urlencode(q),"")).rstrip("?")

def done_urls(instdir):
    # source_url 자체(정규화)로 대조하는 게시판용 (상세 seq 가 없는 edpolicy-intl)
    urls=set()
    for f in glob.glob(os.path.join(REPO,"src/reports",instdir,"*.md")):
        s=open(f,encoding="utf-8").read()
        m=re.search(r'source_url:\s*(\S+)', s)
        if m: urls.add(norm_url(m.group(1)))
    return urls

DONE = {
 "kice-research": done_ids("kice-research", r'seq=(\d+)'),
 "kedi-research": done_ids("kedi-research", r'plNum0=(\d+)'),
 "kosac-research": done_ids("kosac-research", r'/posts/(\d+)'),
 "keris-research": done_ids("keris-research", r'pblcteSeq=(\d+)'),
 "spri": done_ids("spri", r'/posts/view/(\d+)'),
 "keris-issue": done_ids("keris-issue", r'pblcteSeq=(\d+)'),
 "kice-trend": done_ids("kice-trend", r'boardSeq=(\d+)'),
 # --- 추가 게시판 ---
 "kedi-brief": done_ids("kedi-brief", r'article_sq_no=(\d+)'),
 "kosac-trend": done_ids("kosac-trend", r'/posts/(\d+)'),
 "edpolicy-domestic": done_ids("edpolicy-domestic", r'/board/30/(\d+)'),
 "edpolicy-intl": done_urls("edpolicy-intl"),   # 외부 원문 URL 로 대조
}

rows=[]  # 기관코드,기관명,식별자,제목,발행,source_url,관련여부,매칭키워드,요약여부,갱신일

def add(code, name, ident, title, pub, url, force_rel=False, done_key=None):
    # force_rel=True 면 세계 교육 트렌드 수집 대상(9·10·12)이라 키워드 무관 전부 관련.
    hits=match_kw(title)
    rel="o" if (force_rel or hits) else "X"
    key=done_key if done_key is not None else ident
    done="o" if key in DONE.get(code,set()) else "X"
    rows.append([code, name, ident, title, pub, url, rel, ";".join(hits), done, TODAY])

# ================= 크롤러 =================

def crawl_kice_research():
    code,name="kice-research","교육과정평가원 연구보고서"
    seen=set(); page=1
    while page<=120:
        s=get(f"https://www.kice.re.kr/resrchBoard/list.do?cate=0&s=kice&m=030109&page={page}")
        b=s[s.find("<tbody"):s.find("</tbody>")]
        new=0
        for tr in re.split(r"<tr[ >]",b)[1:]:
            m=re.search(r'goView\((\d+)\)',tr)
            t=re.search(r'title="([^"]+)"',tr)
            if not m: continue
            seq=m.group(1)
            if seq in seen: continue
            seen.add(seq); new+=1
            tds=re.findall(r'<td[^>]*>(.*?)</td>',tr,re.S)
            yr=cl(tds[5]) if len(tds)>5 else ""
            url=f"https://www.kice.re.kr/resrchBoard/view.do?seq={seq}&s=kice&m=030109"
            add(code,name,seq,html.unescape(t.group(1)).strip() if t else cl(tds[3]),yr,url)
        if new==0: break
        page+=1
    print(f"{code}: {len(seen)}")

def crawl_kedi_research():
    code,name="kedi-research","교육개발원 연구보고서"
    seen=set()
    for page in range(1,74):
        s=get(f"https://www.kedi.re.kr/khome/main/research/listPubForm.do?maxResults=100&currentPage={page}")
        b=s[s.find("<tbody"):s.find("</tbody>")]
        new=0
        for tr in re.split(r"<tr[ >]",b)[1:]:
            m=re.search(r"selectPubFormFn\('(\d+)'\)",tr)
            if not m: continue
            pl=m.group(1)
            if pl in seen: continue
            seen.add(pl); new+=1
            t=re.search(r"return false;\">(.*?)</a>",tr,re.S)
            tds=re.findall(r'<td[^>]*>(.*?)</td>',tr,re.S)
            yr=cl(tds[2]) if len(tds)>2 else ""
            url=f"https://www.kedi.re.kr/khome/main/research/selectPubForm.do?plNum0={pl}"
            add(code,name,pl,cl(t.group(1)) if t else "",yr[:4],url)
        if new==0: break
    print(f"{code}: {len(seen)}")

def crawl_kosac_research():
    code,name="kosac-research","한국과학창의재단 연구보고서"
    seen=set()
    for page in range(1,8):
        s=get(f"https://www.kosac.re.kr/menus/244/boards/457/posts?page={page}")
        for li in re.split(r'<td class="tit">', s):
            a=re.search(r'<a title="([^"]*)" href="/menus/244/boards/457/posts/(\d+)', li)
            if not a: continue
            pid=a.group(2)
            if pid in seen: continue
            seen.add(pid)
            d=re.search(r'<td class="date">([\d-]{8,10})</td>', li)
            url=f"https://www.kosac.re.kr/menus/244/boards/457/posts/{pid}"
            add(code,name,pid,html.unescape(a.group(1)).strip(),(d.group(1)[:4] if d else ""),url)
    print(f"{code}: {len(seen)}")

def crawl_keris(kind):
    if kind=="research":
        code,name,mi,api="keris-research","한국교육학술정보원 연구보고서","1138","selectPblcteRRList"
        info="selectPblcteRRInfo"
    else:
        code,name,mi,api="keris-issue","한국교육학술정보원 이슈리포트","1139","selectPblcteRMList"
        info="selectPblcteRMInfo"
    seen=set(); page=1
    while page<=40:
        s=get(f"https://keris.or.kr/main/ad/pblcte/{api}.do?mi={mi}&currPage={page}")
        new=0
        for tr in re.split(r"<tr[ >]",s):
            a=re.search(r"pblcteView\('(\d+)'\);\">(.*?)</a>",tr,re.S)
            if not a: continue
            seq=a.group(1)
            if seq in seen: continue
            seen.add(seq); new+=1
            yr=re.search(r'발행년도</strong>\s*(\d{4})',tr,re.S)
            url=f"https://keris.or.kr/main/ad/pblcte/{info}.do?mi={mi}&pblcteSeq={seq}"
            add(code,name,seq,cl(a.group(2)),(yr.group(1) if yr else ""),url)
        if new==0: break
        page+=1
    print(f"{code}: {len(seen)}")

def crawl_spri():
    code,name="spri","소프트웨어정책연구소"
    seen=set()
    for page in range(1,6):
        s=get(f"https://www.spri.kr/posts?data_page={page}&code=data_all&study_type=&board_type=research")
        for li in re.split(r'<li>\s*<div class="box">', s)[1:]:
            vid=re.search(r'/posts/view/(\d+)\?', li)
            title=re.search(r'<div class="title"><a[^>]*>(.*?)</a>', li, re.S)
            if not vid: continue
            v=vid.group(1)
            if v in seen: continue
            seen.add(v)
            d=re.search(r'날짜</span>([\d-]+)', li)
            url=f"https://www.spri.kr/posts/view/{v}?code=research&board_type=research"
            add(code,name,v,cl(title.group(1)) if title else "",(d.group(1)[:4] if d else ""),url)
    print(f"{code}: {len(seen)}")

def crawl_kice_trend():
    code,name="kice-trend","교육과정평가원 국제교육동향"
    seen=set(); page=1
    while page<=30:
        s=get(f"https://www.kice.re.kr/boardCnts/list.do?type=default&page={page}&m=030207&boardID=5000064&s=kice")
        b=s[s.find("<tbody"):s.find("</tbody>")]
        new=0
        for tr in re.split(r"<tr[ >]",b)[1:]:
            a=re.search(r"goView\('(\d+)','(\d+)'",tr)
            t=re.search(r'title="([^"]*)"\s*onclick="javascript:goView',tr)
            if not(a and t): continue
            seq=a.group(2)
            if seq in seen: continue
            seen.add(seq); new+=1
            yr=re.search(r'<td>(\d{4})</td>\s*</tr>',tr)
            url=f"https://www.kice.re.kr/boardCnts/view.do?boardID=5000064&boardSeq={seq}&m=030207&s=kice"
            add(code,name,seq,html.unescape(t.group(1)).strip(),(yr.group(1) if yr else ""),url)
        if new==0: break
        page+=1
    print(f"{code}: {len(seen)}")

def crawl_kedi_brief():
    # 브리프(8): 전 교육주제라 키워드 필터링 (다른 연구보고서와 동일)
    code,name="kedi-brief","교육개발원 브리프"
    seen=set()
    for page in range(1,40):
        s=post("https://www.kedi.re.kr/khome/main/research/kediBriefData.do",{
            "maxResults":"15","maxLinks":"10","currentPage":str(page),"selectTp":"0",
            "isReply":"0","article_sq_no":"","articleSrchKwd":"","isDocSearch":"",
            "board_sq_no":"41","stored_file_type":"1","doc_use_yn":"N","new_disp_days":"0",
            "hot_disp_cnt":"0","anony_use_yn":"N","editor_use_yn":"Y","prvw_use_yn":"N"})
        new=0
        for m in re.finditer(r"goReadSelect\('(\d+)'\)[^>]*>(.*?)</a>", s, re.S):
            sq=m.group(1)
            if sq in seen: continue
            seen.add(sq); new+=1
            title=cl(m.group(2))
            yr=re.search(r'\[(\d{4})년', title)
            url=(f"https://www.kedi.re.kr/khome/main/research/selectKediBriefForm.do?"
                 f"article_sq_no={sq}&board_sq_no=41&maxResults=15&currentPage=1&selectTp=0&isReply=0")
            add(code,name,sq,title,(yr.group(1) if yr else ""),url)
        if new==0: break
    print(f"{code}: {len(seen)}")

def crawl_kosac_trend():
    # 동향리포트(9): 세계 교육 트렌드용 → 전부 관련(force_rel)
    code,name="kosac-trend","한국과학창의재단 동향리포트"
    seen=set()
    for page in range(1,12):
        s=get(f"https://www.kosac.re.kr/menus/248/boards/459/posts?page={page}")
        new=0
        for li in re.split(r'<td class="tit">', s):
            a=re.search(r'<a title="([^"]*)" href="/menus/248/boards/459/posts/(\d+)', li)
            if not a: continue
            pid=a.group(2)
            if pid in seen: continue
            seen.add(pid); new+=1
            d=re.search(r'<td class="date">([\d-]{8,10})</td>', li)
            url=f"https://www.kosac.re.kr/menus/248/boards/459/posts/{pid}"
            add(code,name,pid,html.unescape(a.group(1)).strip(),(d.group(1)[:4] if d else ""),url,force_rel=True)
        if new==0: break
    print(f"{code}: {len(seen)}")

def crawl_edpolicy_domestic():
    # 국가별 교육동향(12): board/30, view(seq) → 상세 = /board/30/<seq>. 전부 관련.
    code,name="edpolicy-domestic","교육정책네트워크 국가별교육동향"
    seen=set(); page=1
    while page<=40:
        s=get(f"https://edpolicy.kedi.re.kr/edpolicy/board/30?pageIndex={page}")
        new=0
        for tr in re.split(r"<tr[ >]", s):
            m=re.search(r"view\((\d+),\s*event\)", tr)
            if not m: continue
            seq=m.group(1)
            if seq in seen: continue
            seen.add(seq); new+=1
            t=re.search(r'class="tit-a"[^>]*>(.*?)</a>', tr, re.S) or re.search(r'view\(\d+, ?event\)[^>]*>(.*?)</a>', tr, re.S)
            d=re.search(r'(\d{4}[.\-]\d{2}[.\-]\d{2})', tr)
            url=f"https://edpolicy.kedi.re.kr/edpolicy/board/30/{seq}"
            add(code,name,seq,cl(t.group(1)) if t else "",(d.group(1)[:4] if d else ""),url,force_rel=True)
        if new==0: break
        page+=1
    print(f"{code}: {len(seen)}")

def crawl_edpolicy_intl():
    # 국제기구동향(10): board/31, 상세페이지 없음 → 외부 원문 URL 이 고유 키. 전부 관련.
    # 과거글은 '월별 주요동향' 내부 상세형이고 최근글만 개별 기사 외부 직링크형이다.
    # 우리 요약 방식(외부 원문 추적)은 외부 직링크형이므로 그 항목만 담는다.
    # 전환기에 외부링크 0인 페이지가 끼어도 끊기지 않도록 연속 2페이지 빈 경우 종료.
    code,name="edpolicy-intl","교육정책네트워크 국제기구동향"
    seen=set(); page=1; empty=0
    while page<=40 and empty<2:
        s=get(f"https://edpolicy.kedi.re.kr/edpolicy/board/31?pageIndex={page}")
        new=0
        for tr in re.split(r"<tr[ >]", s):
            a=re.search(r'<a href="([^"]+)" target="_blank" class="tit-a">(.*?)</a>', tr, re.S)
            if not a: continue
            u=norm_url(a.group(1))
            if u in seen: continue
            seen.add(u); new+=1
            d=re.search(r'(\d{4}[.\-]\d{2}[.\-]\d{2})', tr)
            add(code,name,u,cl(a.group(2)),(d.group(1)[:4] if d else ""),u,force_rel=True,done_key=u)
        empty = empty+1 if new==0 else 0
        page+=1
    print(f"{code}: {len(seen)}")

for fn in [crawl_kice_research, crawl_kedi_research, crawl_kosac_research,
           lambda: crawl_keris("research"), lambda: crawl_keris("issue"),
           crawl_spri, crawl_kice_trend,
           crawl_kedi_brief, crawl_kosac_trend, crawl_edpolicy_domestic, crawl_edpolicy_intl]:
    fn()

os.makedirs(os.path.join(REPO,"data"), exist_ok=True)
out=os.path.join(REPO,"data","report_index.csv")
with open(out,"w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f)
    w.writerow(["기관코드","기관명","식별자","제목","발행","source_url","관련여부","매칭키워드","요약여부","갱신일"])
    w.writerows(rows)

tot=len(rows); rel=sum(1 for r in rows if r[6]=="o"); done=sum(1 for r in rows if r[8]=="o")
rel_done=sum(1 for r in rows if r[6]=="o" and r[8]=="o")
rel_todo=sum(1 for r in rows if r[6]=="o" and r[8]=="X")
print(f"\n총 {tot}행 | 관련 {rel} | 요약완료 {done} | 관련·요약완료 {rel_done} | 관련·미요약 {rel_todo}")
print("→", out)
