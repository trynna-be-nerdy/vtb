import { useQuery } from '@tanstack/react-query'
import { clientFetchBoardMeetings } from './api'

export function useBoardMeetings(board: string, limit = 3) {
  return useQuery({
    queryKey: ['meetings', board, limit],
    queryFn: () => clientFetchBoardMeetings(board, limit),
    staleTime: 60 * 1000,
  })
}
