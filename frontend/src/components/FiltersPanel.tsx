import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Filters } from '@/types';
import { Filter } from 'lucide-react';
interface FiltersPanelProps {
  className?: string;
  onFiltersChange?: (filters: Filters) => void;
}
export const FiltersPanel = ({ className, onFiltersChange }: FiltersPanelProps) => {
  const [filters, setFilters] = useState<Filters>({
    showNetwork: true,
    showSyscall: true,
    showSuspicious: false,
  });
  const handleFilterChange = (key: keyof Filters, value: boolean) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange?.(newFilters);
  };
  return (
    <div className={className}>
      <Card className="h-full bg-card border-border p-4">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
            <Filter className="w-5 h-5 text-primary" />
            Filters
          </h2>
          <p className="text-sm text-muted-foreground">Control what's displayed</p>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="network-filter" className="text-sm text-foreground cursor-pointer">
              Network Events
            </Label>
            <Switch
              id="network-filter"
              checked={filters.showNetwork}
              onCheckedChange={(checked) => handleFilterChange('showNetwork', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Label htmlFor="syscall-filter" className="text-sm text-foreground cursor-pointer">
              Syscall Events
            </Label>
            <Switch
              id="syscall-filter"
              checked={filters.showSyscall}
              onCheckedChange={(checked) => handleFilterChange('showSyscall', checked)}
            />
          </div>
          <div className="border-t border-border my-4"></div>
          <div className="flex items-center justify-between">
            <Label htmlFor="suspicious-filter" className="text-sm text-foreground cursor-pointer">
              Highlight Suspicious
            </Label>
            <Switch
              id="suspicious-filter"
              checked={filters.showSuspicious}
              onCheckedChange={(checked) => handleFilterChange('showSuspicious', checked)}
            />
          </div>
        </div>
        <div className="mt-6 p-3 rounded-lg bg-secondary">
          <div className="text-xs text-muted-foreground space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-success"></div>
              <span>Safe containers</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-warning"></div>
              <span>Warning level</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-destructive"></div>
              <span>Critical threats</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
export default FiltersPanel;
