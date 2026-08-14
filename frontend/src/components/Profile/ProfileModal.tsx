import {
  CheckCircle2,
  Mail,
  ShieldCheck,
  User,
  X,
} from "lucide-react";

import type {
  CurrentUser,
} from "../../types/auth";


interface Props {
  user: CurrentUser;
  onClose: () => void;
}


export default function ProfileModal({
  user,
  onClose,
}: Props) {
  return (
    <div
      className="
        fixed
        inset-0
        z-50
        flex
        items-center
        justify-center
        bg-black/40
        p-4
        backdrop-blur-sm
      "
      onMouseDown={
        onClose
      }
    >
      <div
        className="
          w-full
          max-w-md
          rounded-2xl
          bg-white
          shadow-2xl
        "
        onMouseDown={(
          event
        ) =>
          event.stopPropagation()
        }
      >

        {/* Header */}

        <div className="flex items-center justify-between border-b px-6 py-4">

          <div>
            <h2 className="text-xl font-bold text-gray-900">
              Profile
            </h2>

            <p className="text-sm text-gray-500">
              Your enterprise account details
            </p>
          </div>

          <button
            type="button"
            onClick={
              onClose
            }
            className="
              rounded-lg
              p-2
              text-gray-500
              transition
              hover:bg-gray-100
              hover:text-gray-900
            "
            title="Close"
          >
            <X size={20} />
          </button>

        </div>


        {/* Profile */}

        <div className="p-6">

          {/* Avatar */}

          <div className="mb-6 flex flex-col items-center">

            <div
              className="
                flex
                h-20
                w-20
                items-center
                justify-center
                rounded-full
                bg-blue-100
                text-3xl
                font-bold
                text-blue-700
              "
            >
              {user.full_name
                .trim()
                .charAt(0)
                .toUpperCase()}
            </div>

            <h3 className="mt-3 text-lg font-semibold text-gray-900">
              {user.full_name}
            </h3>

            <span
              className={`
                mt-2
                inline-flex
                items-center
                gap-1
                rounded-full
                px-3
                py-1
                text-xs
                font-medium
                ${
                  user.is_superuser
                    ? (
                      "bg-indigo-100 "
                      + "text-indigo-700"
                    )
                    : (
                      "bg-blue-100 "
                      + "text-blue-700"
                    )
                }
              `}
            >
              <ShieldCheck size={14} />

              {user.is_superuser
                ? "Administrator"
                : "Employee"}
            </span>

          </div>


          {/* Details */}

          <div className="space-y-3">

            <div className="flex items-center gap-3 rounded-xl bg-gray-50 p-4">

              <User
                size={20}
                className="text-gray-500"
              />

              <div>
                <p className="text-xs text-gray-500">
                  Full Name
                </p>

                <p className="font-medium text-gray-900">
                  {user.full_name}
                </p>
              </div>

            </div>


            <div className="flex items-center gap-3 rounded-xl bg-gray-50 p-4">

              <Mail
                size={20}
                className="text-gray-500"
              />

              <div className="min-w-0">

                <p className="text-xs text-gray-500">
                  Email
                </p>

                <p className="truncate font-medium text-gray-900">
                  {user.email}
                </p>

              </div>

            </div>


            <div className="flex items-center gap-3 rounded-xl bg-gray-50 p-4">

              <CheckCircle2
                size={20}
                className={
                  user.is_active
                    ? "text-green-600"
                    : "text-red-600"
                }
              />

              <div>

                <p className="text-xs text-gray-500">
                  Account Status
                </p>

                <p
                  className={
                    user.is_active
                      ? (
                        "font-medium "
                        + "text-green-700"
                      )
                      : (
                        "font-medium "
                        + "text-red-700"
                      )
                  }
                >
                  {user.is_active
                    ? "Active"
                    : "Inactive"}
                </p>

              </div>

            </div>


            <div className="flex items-center gap-3 rounded-xl bg-gray-50 p-4">

              <ShieldCheck
                size={20}
                className="text-gray-500"
              />

              <div>

                <p className="text-xs text-gray-500">
                  Verification
                </p>

                <p className="font-medium text-gray-900">
                  {user.is_verified
                    ? "Verified"
                    : "Not Verified"}
                </p>

              </div>

            </div>

          </div>

        </div>

      </div>
    </div>
  );
}