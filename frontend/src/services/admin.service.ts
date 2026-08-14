import api from "../api/axios";

import {
  API_ENDPOINTS,
} from "../api/endpoints";

import type {
  CreateEmployeeRequest,
  Employee,
  UpdateEmployeeStatusRequest,
} from "../types/admin";


export const adminService = {
  async getEmployees(): Promise<Employee[]> {
    const response =
      await api.get<Employee[]>(
        API_ENDPOINTS.ADMIN_USERS
      );

    return response.data;
  },


  async createEmployee(
    data: CreateEmployeeRequest
  ): Promise<Employee> {
    const response =
      await api.post<Employee>(
        API_ENDPOINTS.ADMIN_USERS,
        data
      );

    return response.data;
  },


  async updateEmployeeStatus(
    employeeId: string,
    data: UpdateEmployeeStatusRequest
  ): Promise<Employee> {
    const response =
      await api.patch<Employee>(
        `${API_ENDPOINTS.ADMIN_USERS}/${employeeId}/status`,
        data
      );

    return response.data;
  },
};