import { useState } from "react";
import { uploadPdf } from "../api/pdfService";

const ACCEPTED_MIME = "application/pdf";

export function useUpload() {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState("");

  const submitFile = async (file) => {
    if (!file) {
      setError("Debes seleccionar un archivo");
      return;
    }
    if (file.type !== ACCEPTED_MIME) {
      setError("Solo se permiten archivos PDF");
      return;
    }

    setError("");
    setIsUploading(true);
    try {
      const data = await uploadPdf(file);
      setUploadResult(data);
    } catch (err) {
      setError(err?.response?.data?.detail ?? "No se pudo subir el archivo");
    } finally {
      setIsUploading(false);
    }
  };

  return {
    isUploading,
    uploadResult,
    error,
    submitFile,
  };
}
