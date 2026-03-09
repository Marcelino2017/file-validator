import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/authService";
import Button from "../components/Button";
import Card from "../components/Card";
import Input from "../components/Input";
import Layout from "../components/Layout";
import { useRegisterForm, validations } from "../hooks/useAuthForm";

export default function RegisterPage() {
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useRegisterForm();

  const onSubmit = async (values) => {
    try {
      await registerUser(values);
      navigate("/login");
    } catch (err) {
      setError("root", {
        message: err?.response?.data?.detail ?? "No fue posible crear el usuario",
      });
    }
  };

  return (
    <Layout>
      <div className="mx-auto max-w-2xl">
        <Card
          title="Registro corporativo"
          subtitle="Completa los datos personales y de la empresa"
        >
          <form
            className="grid gap-4 md:grid-cols-2"
            onSubmit={handleSubmit(onSubmit)}
          >
            <Input
              label="Nombre"
              error={errors.first_name?.message}
              {...register("first_name", { required: "Campo obligatorio" })}
            />
            <Input
              label="Apellido"
              error={errors.last_name?.message}
              {...register("last_name", { required: "Campo obligatorio" })}
            />
            <Input
              label="Cédula"
              error={errors.cedula?.message}
              {...register("cedula", validations.cedula)}
            />
            <Input
              label="NIT"
              error={errors.nit?.message}
              {...register("nit", validations.nit)}
            />
            <Input
              label="Empresa"
              className="md:col-span-2"
              error={errors.enterprise_name?.message}
              {...register("enterprise_name", { required: "Campo obligatorio" })}
            />
            <Input
              label="Contraseña"
              type="password"
              className="md:col-span-2"
              error={errors.password?.message}
              {...register("password", {
                required: "Campo obligatorio",
                minLength: { value: 8, message: "Mínimo 8 caracteres" },
              })}
            />
            {errors.root?.message ? (
              <p className="md:col-span-2 text-sm text-red-700">{errors.root.message}</p>
            ) : null}
            <div className="md:col-span-2 flex items-center justify-between gap-4">
              <Link className="text-sm font-semibold text-brand-700" to="/login">
                Volver al login
              </Link>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Registrando..." : "Crear cuenta"}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </Layout>
  );
}
