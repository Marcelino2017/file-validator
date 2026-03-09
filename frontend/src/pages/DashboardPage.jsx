import { useState } from "react";
import Button from "../components/Button";
import Card from "../components/Card";
import Layout from "../components/Layout";
import { useAuthContext } from "../context/AuthContext";
import { useUpload } from "../hooks/useUpload";

export default function DashboardPage() {
  const { user, signOut } = useAuthContext();
  const { isUploading, uploadResult, error, submitFile } = useUpload();
  const [selectedFile, setSelectedFile] = useState(null);

  const handleUpload = async (event) => {
    event.preventDefault();
    await submitFile(selectedFile);
  };

  return (
    <Layout>
      <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr]">
        <Card
          title={`Bienvenido, ${user?.first_name ?? "Usuario"}`}
          subtitle="Carga y valida documentos PDF con seguridad"
        >
          <div className="space-y-2 text-sm text-brand-700">
            <p>
              <span className="font-semibold text-brand-900">Cédula:</span> {user?.cedula}
            </p>
            <p>
              <span className="font-semibold text-brand-900">Empresa ID:</span>{" "}
              {user?.enterprise_id}
            </p>
          </div>
          <Button className="mt-6 bg-red-700 hover:bg-red-800" onClick={signOut}>
            Cerrar sesión
          </Button>
        </Card>

        <Card title="Subida de PDF" subtitle="Validación por MIME y cabecera binaria">
          <form className="space-y-4" onSubmit={handleUpload}>
            <label className="block rounded-lg border border-dashed border-brand-100 bg-brand-50 px-4 py-6 text-center text-sm text-brand-700">
              <input
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              />
              {selectedFile ? selectedFile.name : "Seleccionar archivo PDF"}
            </label>
            {error ? <p className="text-sm text-red-700">{error}</p> : null}
            {uploadResult ? (
              <div className="rounded-lg bg-green-50 p-3 text-xs text-green-700">
                Documento guardado: {uploadResult.filename}
              </div>
            ) : null}
            <Button type="submit" disabled={isUploading} className="w-full">
              {isUploading ? "Subiendo..." : "Validar y subir"}
            </Button>
          </form>
        </Card>
      </div>
    </Layout>
  );
}
