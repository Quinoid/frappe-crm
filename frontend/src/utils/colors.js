const usedColors = new Set()

export function generateRandomColor() {
  let color
  let attempts = 0 // Counter to prevent infinite loops
  const maxAttempts = 1000 // Arbitrary safety limit

  do {
    if (attempts > maxAttempts) {
      console.warn(
        'Max attempts reached. Clearing usedColors to avoid an infinite loop.',
      )
      usedColors.clear() // Reset the set to allow new colors
    }

    const hue = Math.floor(Math.random() * 360) // 0-360 degrees
    const saturation = Math.floor(Math.random() * 31) + 70 // 70% to 100%
    const lightness = Math.floor(Math.random() * 21) + 50 // 50% to 70%

    // Convert HSL to a CSS-compatible string
    color = `hsl(${hue}, ${saturation}%, ${lightness}%)`

    attempts++
  } while (usedColors.has(color)) // Retry if color is already used

  usedColors.add(color) // Add the unique color to the set
  return color
}
