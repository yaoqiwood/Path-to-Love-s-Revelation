import { get } from '@/api/http'
import { apiUrls } from '@/api/urls'

export const userService = {
  async validateToken(config = {}) {
    return get(apiUrls.users.validateToken(), config)
  }
}

