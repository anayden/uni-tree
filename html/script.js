loadDataText = async (file) => {
  const res = await fetch(file);
  const data = await res.text();
  return data;
};

window.addEventListener("DOMContentLoaded", async () => {
  const data = await loadDataText("uni.dot");
  const images = [...data.matchAll(/img\/u\w{10}.jpg/g)];
  let gv = d3.select("#cy").graphviz();

  images.forEach((img) => {
    console.log("image", img[0]);
    gv = gv.addImage(img[0], "150px", "150px");
  });

  let r = gv.dot(data).render();
});
