import { useMutation, useQuery } from '@tanstack/react-query'
import apiClient from '../lib/api'
import type { MapperResponse, MapperStatsResponse } from '../lib/types'

export const useMapperLookup = () => {
  return useMutation({
    mutationFn: async (section: string) => {
      const response = await apiClient.post<MapperResponse>(
        '/mapper/lookup',
        { section }
      )
      return response.data
    },
  })
}

export const useMapperStats = () => {
  return useQuery({
    queryKey: ['mapperStats'],
    queryFn: async () => {
      const response = await apiClient.get<MapperStatsResponse>('/mapper/stats')
      return response.data
    },
  })
}
