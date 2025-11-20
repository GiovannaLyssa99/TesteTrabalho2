import { Box, Flex, Stack } from '@chakra-ui/react';
import { MiddleSection } from './middle-section';
import { Sidebar } from './sidebar';
import { SidebarProvider } from './sidebar-context';
import { TopSection } from './top-section';

function App() {
  return (
    <SidebarProvider>
      <Flex minH='100dvh'>
        <Sidebar />

        <Box flex='1' bg='#FAF1E4'>
          <Stack h='full'>
            <TopSection />
            <MiddleSection />
          </Stack>
        </Box>
      </Flex>
    </SidebarProvider>
  );
}

export default App;
