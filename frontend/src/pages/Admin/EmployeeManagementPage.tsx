import {
  useState,
  type FormEvent,
} from "react";

import {
  ArrowLeft,
  Eye,
  EyeOff,
  LoaderCircle,
  Plus,
  ShieldCheck,
  UserCheck,
  UserX,
} from "lucide-react";

import {
  useNavigate,
} from "react-router-dom";

import Header from "../../components/Layout/Header";

import {
  useCreateEmployee,
  useEmployees,
  useUpdateEmployeeStatus,
} from "../../hooks/useEmployees";

import {
  useCurrentUser,
} from "../../hooks/useCurrentUser";


export default function EmployeeManagementPage() {
  const navigate =
    useNavigate();

  const {
    data: currentUser,
    isLoading: currentUserLoading,
  } = useCurrentUser();

  const {
    data: employees,
    isLoading,
    error,
  } = useEmployees();

  const createMutation =
    useCreateEmployee();

  const statusMutation =
    useUpdateEmployeeStatus();


  // =====================================================
  // Form State
  // =====================================================

  const [
    showForm,
    setShowForm,
  ] = useState(false);

  const [
    fullName,
    setFullName,
  ] = useState("");

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    showPassword,
    setShowPassword,
  ] = useState(false);


  // =====================================================
  // Create Employee
  // =====================================================

  async function handleCreateEmployee(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (
      !fullName.trim()
      || !email.trim()
      || !password.trim()
    ) {
      return;
    }

    try {
      await createMutation.mutateAsync({
        full_name:
          fullName.trim(),

        email:
          email.trim(),

        password,
      });

      setFullName("");
      setEmail("");
      setPassword("");
      setShowPassword(false);
      setShowForm(false);

    } catch {
      // Error toast is handled by the mutation.
    }
  }


  // =====================================================
  // Employee Status
  // =====================================================

  function handleStatusChange(
    employeeId: string,
    currentStatus: boolean
  ) {
    statusMutation.mutate({
      employeeId,

      isActive:
        !currentStatus,
    });
  }


  // =====================================================
  // Loading Current User
  // =====================================================

  if (currentUserLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <LoaderCircle
          size={26}
          className="animate-spin text-blue-600"
        />
      </div>
    );
  }


  // =====================================================
  // Admin Protection
  // =====================================================

  if (
    !currentUser
    || !currentUser.is_superuser
  ) {
    return (
      <div className="flex h-screen flex-col">

        <Header />

        <div className="flex flex-1 items-center justify-center bg-gray-50 p-6">

          <div className="max-w-md rounded-xl border bg-white p-8 text-center shadow-sm">

            <ShieldCheck
              size={42}
              className="mx-auto mb-4 text-red-500"
            />

            <h2 className="text-xl font-bold text-gray-900">
              Administrator Access Required
            </h2>

            <p className="mt-2 text-sm text-gray-500">
              You do not have permission to manage employees.
            </p>

            <button
              type="button"
              onClick={() =>
                navigate(
                  "/dashboard"
                )
              }
              className="mt-6 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Return to Dashboard
            </button>

          </div>

        </div>

      </div>
    );
  }


  // =====================================================
  // Page
  // =====================================================

  return (
    <div className="flex h-screen flex-col bg-gray-100">

      <Header />

      <main className="flex-1 overflow-y-auto p-6">

        <div className="mx-auto max-w-6xl">

          {/* =================================================
              Page Header
          ================================================= */}

          <div className="mb-6 flex items-center justify-between">

            <div className="flex items-center gap-3">

              <button
                type="button"
                onClick={() =>
                  navigate(
                    "/dashboard"
                  )
                }
                className="rounded-lg border bg-white p-2 hover:bg-gray-50"
                title="Back to Dashboard"
              >
                <ArrowLeft
                  size={20}
                />
              </button>

              <div>

                <h1 className="text-2xl font-bold text-gray-900">
                  Employee Management
                </h1>

                <p className="text-sm text-gray-500">
                  Create and manage enterprise employee access.
                </p>

              </div>

            </div>


            <button
              type="button"
              onClick={() =>
                setShowForm(
                  true
                )
              }
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
            >
              <Plus
                size={18}
              />

              Add Employee
            </button>

          </div>


          {/* =================================================
              Add Employee
          ================================================= */}

          {showForm && (
            <div className="mb-6 rounded-xl border bg-white p-6 shadow-sm">

              <div className="mb-4 flex items-center justify-between">

                <div>

                  <h2 className="text-lg font-semibold text-gray-900">
                    Create Employee Account
                  </h2>

                  <p className="mt-1 text-sm text-gray-500">
                    Create login credentials for a new employee.
                  </p>

                </div>


                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setShowPassword(false);
                  }}
                  className="text-sm text-gray-500 hover:text-gray-900"
                >
                  Cancel
                </button>

              </div>


              <form
                onSubmit={
                  handleCreateEmployee
                }
                className="grid gap-4 md:grid-cols-3"
              >

                {/* Full Name */}

                <div>

                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Full Name
                  </label>

                  <input
                    type="text"
                    value={fullName}
                    onChange={(event) =>
                      setFullName(
                        event.target.value
                      )
                    }
                    className="w-full rounded-lg border p-3 outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Employee name"
                    required
                  />

                </div>


                {/* Email */}

                <div>

                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Work Email
                  </label>

                  <input
                    type="email"
                    value={email}
                    onChange={(event) =>
                      setEmail(
                        event.target.value
                      )
                    }
                    className="w-full rounded-lg border p-3 outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="employee@company.com"
                    required
                  />

                </div>


                {/* Password */}

                <div>

                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Temporary Password
                  </label>

                  <div className="relative">

                    <input
                      type={
                        showPassword
                          ? "text"
                          : "password"
                      }
                      value={password}
                      onChange={(event) =>
                        setPassword(
                          event.target.value
                        )
                      }
                      className="
                        w-full
                        rounded-lg
                        border
                        p-3
                        pr-11
                        outline-none
                        focus:ring-2
                        focus:ring-blue-500
                      "
                      placeholder="Minimum 8 characters"
                      minLength={8}
                      required
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
                        top-1/2
                        -translate-y-1/2
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

                </div>


                {/* Submit */}

                <div className="md:col-span-3">

                  <button
                    type="submit"
                    disabled={
                      createMutation.isPending
                    }
                    className="
                      flex
                      items-center
                      gap-2
                      rounded-lg
                      bg-blue-600
                      px-5
                      py-2
                      text-white
                      hover:bg-blue-700
                      disabled:cursor-not-allowed
                      disabled:opacity-50
                    "
                  >
                    {createMutation.isPending && (
                      <LoaderCircle
                        size={17}
                        className="animate-spin"
                      />
                    )}

                    Create Employee
                  </button>

                </div>

              </form>

            </div>
          )}


          {/* =================================================
              Employee List
          ================================================= */}

          <div className="rounded-xl border bg-white shadow-sm">

            <div className="border-b px-6 py-4">

              <div className="flex items-center justify-between">

                <h2 className="text-lg font-semibold text-gray-900">
                  Employees
                </h2>

                <span className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600">
                  {employees?.length ?? 0}
                </span>

              </div>

            </div>


            {/* Loading */}

            {isLoading && (
              <div className="flex items-center justify-center gap-2 p-10 text-gray-500">

                <LoaderCircle
                  size={20}
                  className="animate-spin"
                />

                Loading employees...

              </div>
            )}


            {/* Error */}

            {error && (
              <div className="p-6 text-red-600">
                Failed to load employees.
              </div>
            )}


            {/* Empty */}

            {!isLoading
              && !error
              && !employees?.length
              && (
                <div className="p-10 text-center text-gray-500">
                  No employees found.
                </div>
              )}


            {/* Table */}

            {employees
              && employees.length > 0
              && (
                <div className="overflow-x-auto">

                  <table className="w-full">

                    <thead className="bg-gray-50">

                      <tr className="text-left text-sm text-gray-600">

                        <th className="px-6 py-3 font-medium">
                          Employee
                        </th>

                        <th className="px-6 py-3 font-medium">
                          Email
                        </th>

                        <th className="px-6 py-3 font-medium">
                          Status
                        </th>

                        <th className="px-6 py-3 text-right font-medium">
                          Action
                        </th>

                      </tr>

                    </thead>


                    <tbody className="divide-y">

                      {employees.map(
                        (employee) => (
                          <tr
                            key={
                              employee.id
                            }
                            className="hover:bg-gray-50"
                          >

                            {/* Employee */}

                            <td className="px-6 py-4">

                              <div className="font-medium text-gray-900">
                                {employee.full_name}
                              </div>

                              <div className="text-xs text-gray-400">
                                Employee
                              </div>

                            </td>


                            {/* Email */}

                            <td className="px-6 py-4 text-sm text-gray-600">
                              {employee.email}
                            </td>


                            {/* Status */}

                            <td className="px-6 py-4">

                              {employee.is_active ? (
                                <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">

                                  <UserCheck
                                    size={14}
                                  />

                                  Active

                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-700">

                                  <UserX
                                    size={14}
                                  />

                                  Inactive

                                </span>
                              )}

                            </td>


                            {/* Action */}

                            <td className="px-6 py-4 text-right">

                              <button
                                type="button"
                                disabled={
                                  statusMutation.isPending
                                }
                                onClick={() =>
                                  handleStatusChange(
                                    employee.id,
                                    employee.is_active
                                  )
                                }
                                className={
                                  employee.is_active
                                    ? "rounded-lg border border-red-200 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
                                    : "rounded-lg border border-green-200 px-3 py-2 text-sm font-medium text-green-600 hover:bg-green-50 disabled:opacity-50"
                                }
                              >
                                {
                                  employee.is_active
                                    ? "Deactivate"
                                    : "Activate"
                                }
                              </button>

                            </td>

                          </tr>
                        )
                      )}

                    </tbody>

                  </table>

                </div>
              )}

          </div>

        </div>

      </main>

    </div>
  );
}