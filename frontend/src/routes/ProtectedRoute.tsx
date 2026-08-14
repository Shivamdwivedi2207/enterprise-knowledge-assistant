import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";

import { authService } from "../services/auth.service";

interface Props {
  children: ReactNode;
}

export default function ProtectedRoute({
  children,
}: Props) {
  const token = authService.getToken();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}