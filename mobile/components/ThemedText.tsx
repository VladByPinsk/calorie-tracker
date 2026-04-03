import { Text, type TextProps } from 'react-native'

export function ThemedText({ style, ...rest }: TextProps) {
  return <Text style={[style]} {...rest} />
}

