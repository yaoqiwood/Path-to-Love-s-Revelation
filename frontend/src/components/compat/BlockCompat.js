export default {
  name: 'BlockCompat',
  setup(_, { slots }) {
    return () => slots.default?.()
  }
}
