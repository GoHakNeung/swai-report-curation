module.exports = {
  layout: "base.njk",
  pagination: {
    data: "institutions",
    size: 1,
    alias: "institution",
    before: (paginationData) => {
      return paginationData.filter((inst) => !inst.link_only);
    },
  },
  eleventyComputed: {
    permalink: (data) => `/institutions/${data.institution.code}/`,
    title: (data) => data.institution.name,
  },
};
