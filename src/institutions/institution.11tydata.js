module.exports = {
  layout: "base.njk",
  pagination: {
    data: "institutions",
    size: 1,
    alias: "institution",
  },
  eleventyComputed: {
    // link_only 기관은 목록 페이지를 만들지 않는다.
    permalink: (data) =>
      data.institution.link_only ? false : `/institutions/${data.institution.code}/`,
    title: (data) => data.institution.name,
  },
};
