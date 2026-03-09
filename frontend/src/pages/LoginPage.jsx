import { Link, useNavigate } from "react-router-dom";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";
import Layout from "../components/Layout";
import { useLoginForm, validations } from "../hooks/useAuthForm";
import { useAuthContext } from "../context/AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const { signIn } = useAuthContext();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useLoginForm();

  const onSubmit = async (values) => {
    try {
      await signIn(values);
      navigate("/dashboard");
    } catch (err) {
      setError("root", {
        message: err?.response?.data?.detail ?? "No se pudo iniciar sesión",
      });
    }
  };

  return (
    <Layout>
      <div className="mx-auto max-w-md">
        <Card title="Ingreso" subtitle="Accede con tu cédula y contraseña">
          <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
            <Input
              label="Cédula"
              placeholder="Ej. 1020304050"
              error={errors.cedula?.message}
              {...register("cedula", validations.cedula)}
            />
            <Input
              label="Contraseña"
              type="password"
              error={errors.password?.message}
              {...register("password", { required: "La contraseña es obligatoria" })}
            />
            {errors.root?.message ? (
              <p className="text-sm text-red-700">{errors.root.message}</p>
            ) : null}
            <Button type="submit" disabled={isSubmitting} className="w-full">
              {isSubmitting ? "Ingresando..." : "Iniciar sesión"}
            </Button>
            <p className="text-center text-sm text-brand-700">
              ¿No tienes cuenta?{" "}
              <Link className="font-semibold text-brand-900" to="/register">
                Regístrate
              </Link>
            </p>
          </form>
        </Card>
      </div>
    </Layout>
  );
}
