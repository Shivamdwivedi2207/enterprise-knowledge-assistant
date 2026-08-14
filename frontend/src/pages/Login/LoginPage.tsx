import {
  useState,
} from "react";

import {
  Eye,
  EyeOff,
} from "lucide-react";

import {
  useNavigate,
} from "react-router-dom";

import {
  useQueryClient,
} from "@tanstack/react-query";

import {
  useForm,
} from "react-hook-form";

import {
  zodResolver,
} from "@hookform/resolvers/zod";

import toast from "react-hot-toast";

import Button from "../../components/Button/Button";
import Input from "../../components/Input/Input";

import {
  authService,
} from "../../services/auth.service";

import {
  loginSchema,
  type LoginFormData,
} from "../../validation/login.schema";


export default function LoginPage() {
  const navigate =
    useNavigate();

  const queryClient =
    useQueryClient();

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    showPassword,
    setShowPassword,
  ] = useState(false);


  const {
    register,
    handleSubmit,
    formState: {
      errors,
    },
  } = useForm<LoginFormData>({
    resolver:
      zodResolver(
        loginSchema
      ),
  });


  async function onSubmit(
    data: LoginFormData
  ) {
    try {
      setLoading(
        true
      );

      const response =
        await authService.login(
          data
        );

      // Remove anything cached for the previous user.
      queryClient.clear();

      // Save new user's JWT.
      authService.saveToken(
        response.access_token
      );

      toast.success(
        "Login Successful"
      );

      navigate(
        "/dashboard",
        {
          replace: true,
        }
      );

    } catch (error: any) {
      console.error(
        error
      );

      let message =
        "Login Failed";

      if (
        error.response
          ?.data
          ?.detail
      ) {
        const detail =
          error.response
            .data
            .detail;

        if (
          typeof detail
          === "string"
        ) {
          message =
            detail;
        }

        else if (
          Array.isArray(
            detail
          )
        ) {
          message =
            detail[0]?.msg
            ?? message;
        }
      }

      toast.error(
        message
      );

    } finally {
      setLoading(
        false
      );
    }
  }


  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">

      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-lg">

        <h1 className="mb-2 text-center text-3xl font-bold">
          Welcome
        </h1>

        <p className="mb-8 text-center text-gray-500">
          Enterprise Knowledge Assistant
        </p>


        <form
          onSubmit={
            handleSubmit(
              onSubmit
            )
          }
          className="space-y-5"
        >

          <Input
            label="Email"
            type="email"
            placeholder="Enter your email"
            {...register(
              "email"
            )}
            error={
              errors.email
                ?.message
            }
          />


          <div className="relative">

            <Input
              label="Password"
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              placeholder="Enter your password"
              {...register(
                "password"
              )}
              error={
                errors.password
                  ?.message
              }
            />

            <button
              type="button"
              onClick={() =>
                setShowPassword(
                  (previous) =>
                    !previous
                )
              }
              className="
                absolute
                right-3
                top-[38px]
                text-gray-500
                transition
                hover:text-gray-800
              "
              title={
                showPassword
                  ? "Hide password"
                  : "Show password"
              }
            >
              {showPassword ? (
                <EyeOff
                  size={19}
                />
              ) : (
                <Eye
                  size={19}
                />
              )}
            </button>

          </div>


          <Button
            type="submit"
            loading={
              loading
            }
          >
            Sign In
          </Button>

        </form>

      </div>

    </div>
  );
}