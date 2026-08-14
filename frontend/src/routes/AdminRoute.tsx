import {
  Navigate,
} from "react-router-dom";

import type {
  ReactNode,
} from "react";

import {
  LoaderCircle,
} from "lucide-react";

import {
  useCurrentUser,
} from "../hooks/useCurrentUser";


interface Props {
  children: ReactNode;
}


export default function AdminRoute({
  children,
}: Props) {
  const {
    data: user,
    isLoading,
    isError,
  } = useCurrentUser();


  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <LoaderCircle
          size={28}
          className="animate-spin text-blue-600"
        />
      </div>
    );
  }


  if (
    isError
    || !user
  ) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }


  if (
    !user.is_superuser
  ) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }


  return (
    <>
      {children}
    </>
  );
}