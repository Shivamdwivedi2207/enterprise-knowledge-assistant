import {
  Bot,
  ChevronDown,
  LogOut,
  ShieldCheck,
  UserRound,
  Users,
} from "lucide-react";

import {
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  useQueryClient,
} from "@tanstack/react-query";

import {
  authService,
} from "../../services/auth.service";

import {
  useCurrentUser,
} from "../../hooks/useCurrentUser";

import ProfileModal from "../Profile/ProfileModal";


export default function Header() {
  const navigate =
    useNavigate();

  const queryClient =
    useQueryClient();

  const {
    data: user,
    isLoading,
  } = useCurrentUser();

  const [
    showProfile,
    setShowProfile,
  ] = useState(false);


  function handleLogout() {
    authService.logout();

    queryClient.clear();

    navigate(
      "/login",
      {
        replace: true,
      }
    );
  }


  function handleManageEmployees() {
    navigate(
      "/admin/employees"
    );
  }


  function getInitial() {
    if (!user?.full_name) {
      return "U";
    }

    return user.full_name
      .trim()
      .charAt(0)
      .toUpperCase();
  }


  return (
    <>
      <header
        className="
          flex
          h-16
          shrink-0
          items-center
          justify-between
          border-b
          border-gray-200
          bg-white
          px-6
          shadow-sm
        "
      >

        {/* Application */}

        <div className="flex items-center gap-3">

          <div
            className="
              flex
              h-10
              w-10
              items-center
              justify-center
              rounded-xl
              bg-blue-600
              text-white
            "
          >
            <Bot size={22} />
          </div>

          <div>

            <h1 className="text-lg font-bold text-gray-900">
              Enterprise Knowledge Assistant
            </h1>

            <p className="text-xs text-gray-500">
              AI-powered knowledge & automation
            </p>

          </div>

        </div>


        {/* Right Side */}

        <div className="flex items-center gap-3">

          {/* Admin Feature */}

          {user?.is_superuser === true && (
            <button
              type="button"
              onClick={
                handleManageEmployees
              }
              className="
                flex
                items-center
                gap-2
                rounded-lg
                bg-indigo-50
                px-3
                py-2
                text-sm
                font-medium
                text-indigo-700
                transition
                hover:bg-indigo-100
              "
            >
              <Users size={17} />

              <span className="hidden md:inline">
                Manage Employees
              </span>
            </button>
          )}


          {/* Name */}

          {!isLoading && user && (
            <div className="hidden text-right md:block">

              <div className="flex items-center justify-end gap-1">

                <p className="text-sm font-medium text-gray-900">
                  {user.full_name}
                </p>

                {user.is_superuser && (
                  <ShieldCheck
                    size={15}
                    className="text-indigo-600"
                  />
                )}

              </div>

              <p className="text-xs text-gray-500">
                {user.is_superuser
                  ? "Administrator"
                  : "Employee"}
              </p>

            </div>
          )}


          {/* Profile Hover Menu */}

          <div className="group relative">

            <button
              type="button"
              className="
                flex
                items-center
                gap-1
                rounded-full
                p-1
                transition
                hover:bg-gray-100
              "
              title="Account"
            >

              <div
                className="
                  flex
                  h-9
                  w-9
                  items-center
                  justify-center
                  rounded-full
                  bg-blue-100
                  font-semibold
                  text-blue-700
                "
              >
                {getInitial()}
              </div>

              <ChevronDown
                size={14}
                className="text-gray-500"
              />

            </button>


            {/* Hover Dropdown */}

            <div
              className="
                invisible
                absolute
                right-0
                top-full
                z-40
                w-64
                pt-2
                opacity-0
                transition
                duration-150
                group-hover:visible
                group-hover:opacity-100
              "
            >

              <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl">

                {user && (
                  <div className="border-b px-4 py-3">

                    <p className="truncate text-sm font-semibold text-gray-900">
                      {user.full_name}
                    </p>

                    <p className="truncate text-xs text-gray-500">
                      {user.email}
                    </p>

                    <p className="mt-1 text-xs font-medium text-blue-600">
                      {user.is_superuser
                        ? "Administrator"
                        : "Employee"}
                    </p>

                  </div>
                )}


                <div className="p-2">

                  <button
                    type="button"
                    onClick={() =>
                      setShowProfile(
                        true
                      )
                    }
                    className="
                      flex
                      w-full
                      items-center
                      gap-3
                      rounded-lg
                      px-3
                      py-2
                      text-left
                      text-sm
                      text-gray-700
                      transition
                      hover:bg-gray-100
                    "
                  >
                    <UserRound
                      size={17}
                    />

                    View Profile
                  </button>


                  <button
                    type="button"
                    onClick={
                      handleLogout
                    }
                    className="
                      flex
                      w-full
                      items-center
                      gap-3
                      rounded-lg
                      px-3
                      py-2
                      text-left
                      text-sm
                      text-red-600
                      transition
                      hover:bg-red-50
                    "
                  >
                    <LogOut
                      size={17}
                    />

                    Logout
                  </button>

                </div>

              </div>

            </div>

          </div>

        </div>

      </header>


      {/* Profile Modal */}

      {showProfile && user && (
        <ProfileModal
          user={
            user
          }
          onClose={() =>
            setShowProfile(
              false
            )
          }
        />
      )}

    </>
  );
}