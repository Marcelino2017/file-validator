import { forwardRef } from "react";

const Input = forwardRef(function Input(
  { label, error, className = "", ...props },
  ref
) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium text-brand-900">{label}</span>
      <input
        ref={ref}
        className={`w-full rounded-lg border border-brand-100 bg-white px-3 py-2 text-sm text-brand-900 outline-none ring-brand-500 transition focus:ring-2 ${className}`}
        {...props}
      />
      {error ? <span className="text-xs text-red-700">{error}</span> : null}
    </label>
  );
});

export default Input;
