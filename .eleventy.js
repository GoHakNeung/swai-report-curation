module.exports = function (eleventyConfig) {
  // _data의 전역 데이터(keywords.json 등)가 보고서 front matter의 동명 필드와
  // 배열 병합(중복)되지 않도록 데이터 캐스케이드 딥 머지를 끈다.
  eleventyConfig.setDataDeepMerge(false);

  // 보고서(.md) 전체를 하나의 컬렉션으로 수집
  eleventyConfig.addCollection("reports", (collectionApi) =>
    collectionApi.getFilteredByGlob("src/reports/**/*.md")
  );

  // institutions.json 을 order 순으로 정렬
  eleventyConfig.addFilter("byOrder", (institutions) =>
    (institutions || []).slice().sort((a, b) => a.order - b.order)
  );

  // front matter의 date(Date 객체)를 yyyy-mm-dd 문자열로 표시
  eleventyConfig.addFilter("ymd", (date) => {
    if (!date) return "";
    const d = date instanceof Date ? date : new Date(date);
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`;
  });

  // 특정 기관의 보고서를 최신순으로 최대 limit건 반환 (기본 6건, 첫 페이지 그리드용)
  eleventyConfig.addFilter("byInstitution", (reports, code, limit = 6) => {
    const filtered = (reports || [])
      .filter((r) => r.data.institution === code)
      .sort((a, b) => {
        const dateA = a.data.date instanceof Date ? a.data.date : new Date(a.data.date);
        const dateB = b.data.date instanceof Date ? b.data.date : new Date(b.data.date);
        return dateB - dateA;
      })
      .slice(0, limit);
    return filtered;
  });

  // JSON 직렬화 필터 (for client-side JS)
  eleventyConfig.addFilter("dump", (data) => {
    const serialized = {
      institutions: data.institutions || [],
      reports: (data.reports || []).map(r => ({
        url: r.url,
        data: {
          institution: r.data.institution,
          title: r.data.title,
          keywords: r.data.keywords || [],
          abstract_excerpt: (r.template || '').substring(0, 150)
        }
      }))
    };
    return JSON.stringify(serialized);
  });

  // 기관 코드로 기관 정보 조회
  eleventyConfig.addFilter("instInfo", (code, institutions) => {
    const inst = (institutions || []).find(i => i.code === code);
    return inst || {};
  });

  // 기관 코드로 기관 이름 조회
  eleventyConfig.addFilter("instName", (code, institutions) => {
    const inst = (institutions || []).find(i => i.code === code);
    return inst ? inst.name : '미분류';
  });

  // 최대 문자수로 자르기
  eleventyConfig.addFilter("limit", (array, count) => {
    return (array || []).slice(0, count);
  });

  return {
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "_site",
    },
    templateFormats: ["njk", "md"],
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};
