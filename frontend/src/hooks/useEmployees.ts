import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import toast from "react-hot-toast";

import {
  adminService,
} from "../services/admin.service";

import type {
  CreateEmployeeRequest,
} from "../types/admin";


export function useEmployees() {
  return useQuery({
    queryKey: [
      "admin-employees",
    ],

    queryFn: () =>
      adminService.getEmployees(),
  });
}


export function useCreateEmployee() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      data: CreateEmployeeRequest
    ) =>
      adminService.createEmployee(
        data
      ),

    onSuccess: async () => {
      toast.success(
        "Employee created successfully"
      );

      await queryClient.invalidateQueries({
        queryKey: [
          "admin-employees",
        ],
      });
    },

    onError: () => {
      toast.error(
        "Failed to create employee"
      );
    },
  });
}


export function useUpdateEmployeeStatus() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      employeeId,
      isActive,
    }: {
      employeeId: string;
      isActive: boolean;
    }) =>
      adminService.updateEmployeeStatus(
        employeeId,
        {
          is_active:
            isActive,
        }
      ),

    onSuccess: async () => {
      toast.success(
        "Employee status updated"
      );

      await queryClient.invalidateQueries({
        queryKey: [
          "admin-employees",
        ],
      });
    },

    onError: () => {
      toast.error(
        "Failed to update employee status"
      );
    },
  });
}