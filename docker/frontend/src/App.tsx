import { Box, Container, Heading, Text, VStack } from '@chakra-ui/react'

function App() {
  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6}>
        <Heading as="h1" size="2xl">MEEMEE</Heading>
        <Text fontSize="xl">AI-Powered Application</Text>
        <Box p={6} borderWidth={1} borderRadius="lg">
          <Text>Welcome to MEEMEE! The application is running successfully.</Text>
        </Box>
      </VStack>
    </Container>
  )
}

export default App 