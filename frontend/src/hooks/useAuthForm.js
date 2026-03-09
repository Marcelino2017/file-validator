import { useForm } from "react-hook-form";

const CEDULA_REGEX = /^[0-9]{6,12}$/;
const NIT_REGEX = /^[0-9]{9,15}(-[0-9])?$/;

export function useLoginForm() {
  return useForm({
    defaultValues: {
      cedula: "",
      password: "",
    },
  });
}

export function useRegisterForm() {
  return useForm({
    defaultValues: {
      first_name: "",
      last_name: "",
      cedula: "",
      enterprise_name: "",
      nit: "",
      password: "",
    },
  });
}

export const validations = {
  cedula: {
    required: "La cédula es obligatoria",
    pattern: {
      value: CEDULA_REGEX,
      message: "Formato de cédula inválido (6-12 dígitos)",
    },
  },
  nit: {
    required: "El NIT es obligatorio",
    pattern: {
      value: NIT_REGEX,
      message: "Formato de NIT inválido (9-15 dígitos y opcional -X)",
    },
  },
};
