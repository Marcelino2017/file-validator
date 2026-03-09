import axiosClient from "./axiosClient";

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await axiosClient.post("/documents/upload-pdf", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return data;
}
