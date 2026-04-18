import { useMutation, useQuery } from '@tanstack/react-query'
import apiClient from '../lib/api'
import type { ProfileListResponse, ProfileResponse } from '../lib/types'

export const useProfiles = () => {
  return useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.get<ProfileListResponse>('/profiles')
      return response.data
    },
  })
}

export const useProfileAnalysis = () => {
  return useMutation({
    mutationFn: async (profileType: string) => {
      const response = await apiClient.post<ProfileResponse>(
        '/profiles/analyze',
        { profile_type: profileType }
      )
      return response.data
    },
  })
}
