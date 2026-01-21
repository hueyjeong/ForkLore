import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AICopilotPanel } from './ai-copilot-panel';
import * as aiApi from '@/lib/api/ai.api';

// Mock the API module
vi.mock('@/lib/api/ai.api', () => ({
  getWikiSuggestions: vi.fn(),
  checkConsistency: vi.fn(),
}));

// Mock UI components
vi.mock('@/components/ui/sheet', () => {
  const MockSheet = ({ children, open, onOpenChange }: any) => {
    return open ? <div data-testid="sheet-root">{children}</div> : null;
  };
  return {
    Sheet: MockSheet,
    SheetContent: ({ children }: any) => <div data-testid="sheet-content">{children}</div>,
    SheetHeader: ({ children }: any) => <div data-testid="sheet-header">{children}</div>,
    SheetTitle: ({ children }: any) => <div data-testid="sheet-title">{children}</div>,
    SheetDescription: ({ children }: any) => <div data-testid="sheet-description">{children}</div>,
    SheetFooter: ({ children }: any) => <div data-testid="sheet-footer">{children}</div>,
  };
});

// Mock Tabs components since they might rely on Context
vi.mock('@/components/ui/tabs', () => {
    return {
        Tabs: ({ children, value, onValueChange }: any) => <div data-testid="tabs-root">{children}</div>,
        TabsList: ({ children }: any) => <div data-testid="tabs-list">{children}</div>,
        TabsTrigger: ({ children, value, onClick }: any) => (
            <button data-testid={`tab-trigger-${value}`} onClick={onClick}>
                {children}
            </button>
        ),
        TabsContent: ({ children, value }: any) => <div data-testid={`tab-content-${value}`}>{children}</div>,
    }
});

describe('AICopilotPanel', () => {
  const mockOnClose = vi.fn();
  const mockOnApplySuggestion = vi.fn();
  const defaultProps = {
    branchId: 123,
    chapterContent: 'This is some chapter content.',
    isOpen: true,
    onClose: mockOnClose,
    onApplySuggestion: mockOnApplySuggestion,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly when open', () => {
    render(<AICopilotPanel {...defaultProps} />);
    expect(screen.getByTestId('sheet-content')).toBeInTheDocument();
    // Use getByTestId for title to avoid ambiguity
    expect(screen.getByTestId('sheet-title')).toHaveTextContent('AI Copilot');
  });

  it('does not trigger analysis automatically', () => {
    render(<AICopilotPanel {...defaultProps} />);
    expect(aiApi.getWikiSuggestions).not.toHaveBeenCalled();
    expect(aiApi.checkConsistency).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: /분석하기/i })).toBeInTheDocument();
  });

  it('triggers analysis when button is clicked', async () => {
    const mockWikiSuggestions = { data: [] };
    const mockConsistencyCheck = { consistent: true, issues: [] };
    
    (aiApi.getWikiSuggestions as any).mockResolvedValue(mockWikiSuggestions);
    (aiApi.checkConsistency as any).mockResolvedValue(mockConsistencyCheck);

    render(<AICopilotPanel {...defaultProps} />);
    
    const analyzeButton = screen.getByRole('button', { name: /분석하기/i });
    fireEvent.click(analyzeButton);

    await waitFor(() => {
      // Check that the correct arguments are passed based on the component implementation
      expect(aiApi.getWikiSuggestions).toHaveBeenCalledWith(123, { text: 'This is some chapter content.' });
      expect(aiApi.checkConsistency).toHaveBeenCalledWith(123, { chapter_id: 123 });
    });
  });

  it('displays suggestions and allows accept/reject', async () => {
    const mockSuggestion = { name: 'New Character', description: 'A new hero' };
    const mockWikiSuggestions = { data: [mockSuggestion] };
    const mockConsistencyCheck = { consistent: true, issues: [] };
    
    (aiApi.getWikiSuggestions as any).mockResolvedValue(mockWikiSuggestions);
    (aiApi.checkConsistency as any).mockResolvedValue(mockConsistencyCheck);

    render(<AICopilotPanel {...defaultProps} />);
    
    // Trigger analysis
    fireEvent.click(screen.getByRole('button', { name: /분석하기/i }));

    await waitFor(() => {
        expect(screen.getByText('New Character')).toBeInTheDocument();
        expect(screen.getByText('A new hero')).toBeInTheDocument();
    });

    // Accept suggestion
    const acceptBtn = screen.getByRole('button', { name: /Accept suggestion/i }); // Using aria-label
    fireEvent.click(acceptBtn);
    expect(mockOnApplySuggestion).toHaveBeenCalledWith(mockSuggestion);

    // Reject suggestion
    const rejectBtn = screen.getByRole('button', { name: /Reject suggestion/i }); // Using aria-label
    fireEvent.click(rejectBtn);
    
    await waitFor(() => {
        expect(screen.queryByText('New Character')).not.toBeInTheDocument();
    });
  });

  it('displays consistency issues', async () => {
     const mockWikiSuggestions = { data: [] };
     const mockConsistencyCheck = { consistent: false, issues: ['Timeline error'] };
     
     (aiApi.getWikiSuggestions as any).mockResolvedValue(mockWikiSuggestions);
     (aiApi.checkConsistency as any).mockResolvedValue(mockConsistencyCheck);
 
     render(<AICopilotPanel {...defaultProps} />);
     
     fireEvent.click(screen.getByRole('button', { name: /분석하기/i }));
 
     await waitFor(() => {
         // Since tabs are mocked, both contents might be rendered or we check existence
         // My mock implementation renders all TabsContent divs but typical tabs only render active
         // However, my mock: TabsContent: ({ children, value }: any) => <div data-testid={`tab-content-${value}`}>{children}</div>
         // It renders children unconditionally? 
         // Real Tabs only render content when active.
         // But my mock is simple. Let's check if the element exists.
         // In the real component, 'wiki' is default. I might need to click the tab trigger.
     });

     // Wait, the component sets activeTab state. My mock needs to support that if I want to switch tabs.
     // Or I can just inspect the DOM if my mock renders everything.
     // But wait, the component uses `Tabs value={activeTab} onValueChange={setActiveTab}`.
     // If my mock ignores `value` and renders everything, then I can find it.
     // If my mock respects it...
     // The mock I wrote: `TabsContent` renders a div. It doesn't check if `active` matches `value`.
     // So all contents are rendered in the test.
     
     expect(screen.getByText('Timeline error')).toBeInTheDocument();
     expect(screen.getByText('Inconsistencies found')).toBeInTheDocument();
  });
});
