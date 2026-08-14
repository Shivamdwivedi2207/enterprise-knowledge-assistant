import {
  useQuery,
} from "@tanstack/react-query";

import {
  authService,
} from "../services/auth.service";

import type {
  CurrentUser,
} from "../types/auth";


export function useCurrentUser() {
  return useQuery<CurrentUser>({
    queryKey: [
      "current-user",
    ],

    queryFn: () =>
      authService.me(),

    staleTime:
      5 * 60 * 1000,
  });
}