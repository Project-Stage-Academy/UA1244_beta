import { render, screen, cleanup } from '@testing-library/react';
import App from './App';

afterEach(cleanup);

describe('App Component', () => {
  test('renders learn react link', () => {
    render(<App />);
    const linkElement = screen.getByRole('link', { name: /learn react/i });
    expect(linkElement).toBeInTheDocument();
  });

  test('has the correct href value', () => {
    render(<App />);
    const linkElement = screen.getByRole('link', { name: /learn react/i });
    expect(linkElement).toHaveAttribute('href', 'https://reactjs.org');
  });

  test('has the correct CSS class', () => {
    render(<App />);
    const linkElement = screen.getByRole('link', { name: /learn react/i });
    expect(linkElement).toHaveClass('your-css-class');
  });

  it('matches snapshot', () => {
    const { asFragment } = render(<App />);
    expect(asFragment()).toMatchSnapshot();
  });
});





