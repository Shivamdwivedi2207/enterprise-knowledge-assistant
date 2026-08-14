export interface Employee {
  id: string;
  full_name: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
}


export interface CreateEmployeeRequest {
  full_name: string;
  email: string;
  password: string;
}


export interface UpdateEmployeeStatusRequest {
  is_active: boolean;
}