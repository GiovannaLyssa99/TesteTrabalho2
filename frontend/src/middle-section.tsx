import {
  Center,
  Heading,
  IconButton,
  Input,
  VStack,
  Text,
  Spinner,
  Flex,  
  Box,  
} from '@chakra-ui/react';
import {
  FileUploadList,
  FileUploadRoot,
  FileUploadTrigger,
} from './components/ui/file-button';
import { InputGroup } from './components/ui/input-group';
import {
  EnterIcon,
  UploadIcon,
} from './icons/other-icons';
import { useState } from 'react';
import axios from 'axios';

interface Message {
  role: 'user' | 'bot' | 'error';
  content: string;
}

export function MiddleSection() {
  const [inputValue, setInputValue] = useState('');
  
  const [messages, setMessages] = useState<Message[]>([]); 
  const [isLoading, setIsLoading] = useState(false);

  const handleInputValue = (e) => {
    setInputValue(e.target.value);
  };

  const handleSendMessage = async () => {
    if (inputValue.trim() === '') {
      return;
    }

    const userQuery = inputValue;

    setMessages(prevMessages => [...prevMessages, { role: 'user', content: userQuery }]);
    setInputValue(''); 
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        query: userQuery,
      });

      const botAnswer = response.data.answer;

      setMessages(prevMessages => [...prevMessages, { role: 'bot', content: botAnswer }]);

    } catch (error) {
      console.error("Erro ao enviar mensagem:", error);
     
      setMessages(prevMessages => [...prevMessages, { 
        role: 'error', 
        content: "Desculpe, não foi possível obter uma resposta no momento." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <Flex direction='column' flex='1' bg='#FAF1E4' h="100vh">
    
      <VStack 
          flex='1' 
          gap='4' 
          overflowY='auto' 
          p='6'
          maxW="860px" 
          mx="auto" 
          w="full"
          alignItems="flex-start" 
      >
    
          {messages.length === 0 && (
              <Center h="full" w="full">
                  <Heading size='3xl' color="#E3661D" textAlign="center">Como posso te ajudar?</Heading>
              </Center>
          )}

        
          {messages.map((message, index) => (
              <Box 
                  key={index} 
                  
                  alignSelf={message.role === 'user' ? 'flex-end' : 'flex-start'} 
                  maxW="80%"
                  p="3"
                  borderRadius="lg"
                  
                  bg={message.role === 'user' ? '#E3661D' : 'white'} 
                  color={message.role === 'user' ? 'white' : '#333'}
                  boxShadow="md"
                  
                  border={message.role === 'error' ? '1px solid red' : 'none'}
              >
                  <Text whiteSpace="pre-wrap"> 
                      {message.content}
                  </Text>
              </Box>
          ))}

         
          {isLoading && (
              <Flex 
                  alignSelf='flex-start' 
                  p="3" 
                  bg="white" 
                  borderRadius="lg" 
                  boxShadow="md"
                  alignItems="center"
              >
                  <Spinner size="sm" color="#E3661D" mr="2" />
                  <Text color="#333">Digitando...</Text>
              </Flex>
          )}
      </VStack>

      <Center 
          w='full' 
          p={4} 
          bg='#e28a57' 
          borderTop="1px solid #ddd" 
          boxShadow="lg"
          position="sticky" 
          bottom="0" 
          zIndex="10"
      >
          <InputGroup
              minW='768px'
              maxW="860px" 
              startElement={
                  <FileUploadRoot>
                      <FileUploadTrigger asChild>
                          <UploadIcon fontSize='2xl' color='fg' />
                      </FileUploadTrigger>
                      <FileUploadList />
                  </FileUploadRoot>
              }
              endElement={
                  <IconButton
                      bg='#E3661D'
                      fontSize='2xl'
                      size='sm'
                      borderRadius='full'
                      disabled={inputValue.trim() === '' || isLoading}
                      onClick={handleSendMessage}
                  >
                      <EnterIcon fontSize='2xl' />
                  </IconButton>
              }
          >
              <Input
                  placeholder='Envie uma mensagem...'
                  variant='subtle'
                  size='lg'
                  borderRadius='3xl'
                  value={inputValue}
                  onChange={handleInputValue}
                  onKeyDown={handleKeyDown}
                  _placeholder={{ color: '#F9CE91' }}
                  _focus={{ borderColor: '#E3661D' }}
                  isDisabled={isLoading} 
              />
          </InputGroup>
      </Center>
    </Flex>
  );
}